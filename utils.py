import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import hashlib
import time
import json
import pickle
import os
from datetime import datetime, timedelta

# 内存缓存配置
MEMORY_CACHE_SIZE = 2000  # 内存缓存最大条目数
MEMORY_CACHE_TTL_HOURS = 24  # 内存缓存过期时间（小时）

def filter_dataframe(df, filters):
    """根据筛选条件过滤DataFrame"""
    filtered_df = df.copy()
    
    for filter_type, filter_value in filters.items():
        if filter_value and filter_value != '全部':
            if filter_type == 'Brand':
                filtered_df = filtered_df[filtered_df['Brand'] == filter_value]
            elif filter_type == 'Asin':
                filtered_df = filtered_df[filtered_df['Asin'] == filter_value]
            elif filter_type == 'Rating':
                filtered_df = filtered_df[filtered_df['Rating'] == filter_value]
            elif filter_type == 'Review Type':
                filtered_df = filtered_df[filtered_df['Review Type'] == filter_value]
            elif filter_type == 'row_range':
                start_row, end_row = filter_value
                filtered_df = filtered_df.iloc[start_row:end_row]
    
    return filtered_df

def process_data(df, brand_df=None):
    """数据预处理函数"""
    # 确保所需列存在
    required_columns = ['Asin', 'Title', 'Content', 'Model', 'Rating', 'Date']
    if not all(col in df.columns for col in required_columns):
        st.error(f"缺少必要的列: {[col for col in required_columns if col not in df.columns]}")
        return None
    
    # 只保留必要的列
    df = df[required_columns].copy()
    
    # 向量化操作
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # 使用str.strip()的向量化操作
    text_columns = ['Title', 'Content', 'Model']
    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()
    
    # 添加ID列（确保唯一性）
    df.insert(0, 'ID', range(1, len(df) + 1))
    
    # 使用向量化操作替代apply
    df['Review Type'] = pd.cut(
        df['Rating'],
        bins=[-float('inf'), 2, 3, float('inf')],
        labels=['negative', 'neutral', 'positive']
    )
    
    # 如果提供了品牌数据，进行关联
    if brand_df is not None and 'ASIN' in brand_df.columns and 'Brand' in brand_df.columns:
        # 清理品牌数据
        brand_columns = ['ASIN', 'Brand']
        if 'Parent ASIN' in brand_df.columns:
            brand_columns.append('Parent ASIN')
        
        brand_df = brand_df[brand_columns].copy()
        brand_df['ASIN'] = brand_df['ASIN'].astype(str).str.strip()
        brand_df['Brand'] = brand_df['Brand'].astype(str).str.strip()
        if 'Parent ASIN' in brand_df.columns:
            brand_df['Parent ASIN'] = brand_df['Parent ASIN'].astype(str).str.strip()
        
        # 处理重复的ASIN，保留最新的品牌信息
        brand_df = brand_df.drop_duplicates(subset=['ASIN'], keep='last')
        
        # 备份原始ID
        original_ids = df['ID'].copy()
        
        # 第一轮：通过ASIN关联品牌信息
        df = df.merge(brand_df[['ASIN', 'Brand']], left_on='Asin', right_on='ASIN', how='left')
        
        # 统计第一轮匹配结果
        first_round_matches = df['Brand'].notna().sum()
        
        # 第二轮：如果第一轮没有匹配上，且存在Parent ASIN，则用Parent ASIN连接
        if 'Parent ASIN' in brand_df.columns and first_round_matches < len(df):
            # 找出第一轮没有匹配上的记录
            unmatched_mask = df['Brand'].isna()
            unmatched_df = df[unmatched_mask].copy()
            
            if len(unmatched_df) > 0:
                # 创建Parent ASIN连接用的品牌数据
                parent_brand_df = brand_df[brand_df['Parent ASIN'].notna()].copy()
                parent_brand_df = parent_brand_df[['Parent ASIN', 'Brand']].rename(columns={'Parent ASIN': 'ASIN'})
                
                # 通过Parent ASIN进行第二轮连接
                unmatched_df = unmatched_df.merge(parent_brand_df, left_on='Asin', right_on='ASIN', how='left', suffixes=('', '_parent'))
                
                # 更新原数据中未匹配的记录
                df.loc[unmatched_mask, 'Brand'] = unmatched_df['Brand']
                
                # 清理多余的列
                if 'ASIN_y' in df.columns:
                    df = df.drop(columns=['ASIN_y'])
                if 'ASIN_parent' in df.columns:
                    df = df.drop(columns=['ASIN_parent'])
        
        # 恢复原始ID
        df['ID'] = original_ids
        
        # 统计最终匹配结果
        final_matches = df['Brand'].notna().sum()
        total_records = len(df)
        match_rate = (final_matches / total_records * 100) if total_records > 0 else 0
        
        st.success(f"✅ 成功关联品牌数据！")
        st.info(f"📊 匹配统计：")
        st.info(f"   - 总记录数：{total_records}")
        st.info(f"   - 成功匹配：{final_matches}")
        st.info(f"   - 匹配率：{match_rate:.1f}%")
        
        if 'Parent ASIN' in brand_df.columns:
            st.info(f"   - 第一轮ASIN匹配：{first_round_matches}")
            st.info(f"   - 第二轮Parent ASIN匹配：{final_matches - first_round_matches}")
    
    # 重新排序列
    column_order = ['ID', 'Asin', 'Brand', 'Title', 'Content', 'Model', 'Rating', 'Date', 'Review Type']
    existing_columns = [col for col in column_order if col in df.columns]
    df = df[existing_columns]
    
    return df

def calculate_review_stats(df):
    """计算评论类型的统计信息"""
    # 计算各类型数量
    review_counts = df['Review Type'].value_counts()
    
    # 计算百分比
    review_percentages = (review_counts / len(df) * 100).round(2)
    
    # 合并统计信息
    stats_df = pd.DataFrame({
        '数量': review_counts,
        '占比(%)': review_percentages
    })
    
    return stats_df, review_counts, review_percentages

def create_pie_chart(review_counts, title='评论类型分布'):
    # 确保索引顺序与颜色映射一致
    review_counts = review_counts.reindex(
        ['positive', 'neutral', 'negative'], 
        fill_value=0
    )
    
    # 创建数据框确保顺序
    df = pd.DataFrame({
        'type': review_counts.index,
        'count': review_counts.values
    })
    
    fig = px.pie(
        df,
        values='count',
        names='type',
        title=title,
        color='type',  # 关键：通过color参数指定分组
        color_discrete_map={
            'positive': '#2ECC71',  # 绿色
            'neutral': '#F1C40F',   # 黄色
            'negative': '#E74C3C'   # 红色
        },
        category_orders={'type': ['positive', 'neutral', 'negative']}
    )
    
    # 禁用主题干扰
    fig.update_layout(template='none')
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=1))  # 添加白色边框
    )
    return fig

def analyze_by_group(df, group_by):
    """按指定字段进行分组分析"""
    # 使用更高效的分组操作
    if isinstance(group_by, list):
        if 'Brand' in group_by:
            df['Group'] = df['Brand'] + ' - ' + df['Asin'] + ' - ' + df['Model']
        else:
            df['Group'] = df['Asin'] + ' - ' + df['Model']
        group_by = 'Group'
    
    # 一次性计算所有统计信息
    stats = df.groupby(group_by).agg({
        'Rating': ['count', 'mean', 'std'],
        'Review Type': lambda x: x.value_counts().to_dict()
    }).round(2)
    
    # 重命名列
    stats.columns = ['评论数量', '平均评分', '标准差', '评论类型分布']
    
    # 计算评分分布
    rating_dist = pd.crosstab(df[group_by], df['Rating'], normalize='index') * 100
    
    return stats, rating_dist, group_by

def create_rating_trend_chart(df, group_by):
    """创建评分趋势图"""
    # 使用更高效的时间处理
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    trend_data = df.groupby(['Month', group_by])['Rating'].mean().reset_index()
    
    # 创建趋势图
    title = f'{group_by}随时间的平均评分变化'
    
    fig = px.line(trend_data, 
                  x='Month', 
                  y='Rating', 
                  color=group_by,
                  title=title,
                  labels={'Rating': '平均评分', 'Month': '月份'})
    
    fig.update_xaxes(tickangle=45)
    return fig

def create_rating_heatmap(rating_dist_pct, title):
    """创建评分分布热力图"""
    fig = go.Figure(data=go.Heatmap(
        z=rating_dist_pct.values,
        x=rating_dist_pct.columns,
        y=rating_dist_pct.index,
        colorscale='RdYlGn',
        text=rating_dist_pct.round(1).values,
        texttemplate='%{text}%',
        textfont={"size": 10},
        hoverongaps=False))
    
    fig.update_layout(
        title=title,
        xaxis_title='评分',
        yaxis_title='产品',
        height=max(300, len(rating_dist_pct) * 30))
    
    return fig

def create_rating_pie_chart(rating_dist_pct, title):
    """创建评分分布饼图"""
    # 创建一个空的图表列表
    figs = []
    
    # 定义颜色映射 - 确保星级和颜色一一对应
    color_map = {
        5: 'rgb(0, 128, 0)',      # 绿色 - 5星
        4: 'rgb(135, 206, 235)',  # 浅蓝色 - 4星
        3: 'rgb(255, 215, 0)',    # 黄色 - 3星
        2: 'rgb(255, 0, 0)',      # 红色 - 2星
        1: 'rgb(139, 0, 0)'       # 深红色 - 1星
    }
    
    # 为每个ASIN或ASIN+Model创建饼图
    for idx, row in rating_dist_pct.iterrows():
        # 创建数据框
        df_pie = pd.DataFrame({
            '评分': row.index,
            '占比': row.values
        })
        
        # 过滤掉占比为0的数据
        df_pie = df_pie[df_pie['占比'] > 0]
        
        # 确保评分按降序排列
        df_pie = df_pie.sort_values('评分', ascending=False)
        
        # 使用go.Figure直接创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=df_pie['评分'],
            values=df_pie['占比'],
            hole=0.3,
            marker=dict(
                colors=[color_map[rating] for rating in df_pie['评分']],
                line=dict(color='#FFFFFF', width=1)
            ),
            textinfo='percent+label',
            textposition='outside',
            textfont_size=14,
            insidetextorientation='horizontal',
            hovertemplate='%{label}: %{percent:.1%}<extra></extra>',
            texttemplate='%{label}<br>%{percent:.1%}'
        )])
        
        # 更新布局
        fig.update_layout(
            title=f'{idx} 评分分布',
            showlegend=False,  # 去除图例
            margin=dict(t=50, b=50, l=50, r=50),  # 调整边距
            uniformtext_minsize=12,  # 设置最小文本大小
            uniformtext_mode='hide'  # 隐藏太小的文本
        )
        
        # 优化标签位置和显示
        fig.update_traces(
            textposition='outside',
            textinfo='percent+label',
            rotation=0  # 从0度开始
        )
        
        figs.append(fig)
    
    return figs

def save_fig_to_html(fig, filename):
    """保存图表为HTML文件"""
    return fig.to_html()

def get_download_data(df, file_format='excel'):
    """准备下载数据"""
    if file_format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        data = output.getvalue()
        return data
    else:  # txt format
        # 将DataFrame转换为格式化的文本
        output = io.StringIO()
        
        # 写入表头
        headers = df.columns.tolist()
        output.write('\t'.join(headers) + '\n')
        output.write('-' * 100 + '\n')  # 分隔线
        
        # 写入数据行
        for _, row in df.iterrows():
            # 确保所有值都转换为字符串，并处理可能的空值
            row_values = [str(val) if pd.notna(val) else '' for val in row]
            # 使用制表符分隔，这样在文本编辑器中会对齐
            output.write('\t'.join(row_values) + '\n')
        
        return output.getvalue().encode('utf-8')

# 腾讯翻译API相关函数
class TencentTranslator:
    """腾讯翻译API封装类"""
    
    def __init__(self, secret_id, secret_key, region='ap-beijing'):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        
    def translate(self, text, source='en', target='zh'):
        """翻译文本（带缓存）"""
        # 生成缓存键
        cache_key = get_memory_cache_key(text, 'tencent', source, target)
        
        # 尝试从缓存加载
        cached_result = load_from_memory_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            from tencentcloud.common import credential
            from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
            from tencentcloud.tmt.v20180321 import tmt_client, models
            
            # 实例化一个认证对象
            cred = credential.Credential(self.secret_id, self.secret_key)
            
            # 实例化要请求产品的client对象
            client = tmt_client.TmtClient(cred, self.region)
            
            # 实例化一个请求对象
            req = models.TextTranslateRequest()
            
            # 设置请求参数
            req.SourceText = text
            req.Source = source
            req.Target = target
            req.ProjectId = 0
            
            # 通过client对象调用想要访问的接口
            resp = client.TextTranslate(req)
            
            # 保存到缓存
            save_to_memory_cache(cache_key, resp.TargetText)
            
            # 返回翻译结果
            return resp.TargetText
                
        except TencentCloudSDKException as err:
            raise Exception(f"腾讯翻译API调用失败: {err}")
        except Exception as e:
            raise Exception(f"腾讯翻译API调用失败: {str(e)}")

def create_translator(engine='google', secret_id=None, secret_key=None):
    """创建翻译器实例"""
    if engine == 'google':
        return CachedGoogleTranslator(source='en', target='zh-CN')
    elif engine == 'tencent':
        if not secret_id or not secret_key:
            raise ValueError("腾讯翻译API需要提供SecretId和SecretKey")
        return TencentTranslator(secret_id, secret_key)
    else:
        raise ValueError(f"不支持的翻译引擎: {engine}")

class CachedGoogleTranslator:
    """带缓存的Google翻译器"""
    
    def __init__(self, source='en', target='zh-CN'):
        from deep_translator import GoogleTranslator
        self.translator = GoogleTranslator(source=source, target=target)
        
    def translate(self, text, source='en', target='zh-CN'):
        """翻译文本（带缓存）"""
        # 生成缓存键
        cache_key = get_memory_cache_key(text, 'google', source, target)
        
        # 尝试从缓存加载
        cached_result = load_from_memory_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 调用Google翻译
        result = self.translator.translate(text)
        
        # 保存到缓存
        save_to_memory_cache(cache_key, result)
        
        return result 

# ========== AI批量标注缓存与统一调用工具 ==========
import hashlib
AI_CACHE_DIR = "ai_label_cache"
os.makedirs(AI_CACHE_DIR, exist_ok=True)

def get_ai_cache_key(text, prompt, model):
    key = f"{text}_{prompt}_{model}"
    return hashlib.md5(key.encode('utf-8')).hexdigest()

def save_ai_label_to_cache(cache_key, label):
    with open(os.path.join(AI_CACHE_DIR, f"{cache_key}.pkl"), "wb") as f:
        pickle.dump(label, f)

def load_ai_label_from_cache(cache_key):
    path = os.path.join(AI_CACHE_DIR, f"{cache_key}.pkl")
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except:
            return None
    return None

def call_ai_model(text, prompt, model, api_key, max_retries=3):
    for attempt in range(max_retries):
        try:
            # 处理prompt格式化，支持多种占位符格式
            try:
                if "{text}" in prompt:
                    formatted_prompt = prompt.format(text=text)
                elif "{Content}" in prompt:
                    formatted_prompt = prompt.format(Content=text)
                else:
                    # 如果没有占位符，直接使用prompt
                    formatted_prompt = prompt
            except Exception:
                # 如果格式化失败，直接使用prompt
                formatted_prompt = prompt
            
            if model == "OpenAI":
                import openai
                openai.api_key = api_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": formatted_prompt}],
                    temperature=0
                )
                return response['choices'][0]['message']['content'].strip()
            elif model == "Deepseek":
                import openai
                version = getattr(openai, '__version__', '0.0.0')
                if version.startswith('1.'):
                    # openai >=1.0.0
                    client = openai.OpenAI(
                        api_key=api_key,
                        base_url="https://api.deepseek.com/v1"
                    )
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": formatted_prompt}],
                        temperature=0,
                        max_tokens=1000
                    )
                    return response.choices[0].message.content.strip()
                else:
                    # openai 0.x 兼容写法
                    openai.api_key = api_key
                    openai.api_base = "https://api.deepseek.com/v1"
                    response = openai.ChatCompletion.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": formatted_prompt}],
                        temperature=0
                    )
                    return response['choices'][0]['message']['content'].strip()
            elif model == "阿里千问":
                import dashscope
                rsp = dashscope.Generation.call(
                    model="qwen-turbo",
                    api_key=api_key,
                    messages=[{"role": "user", "content": formatted_prompt}]
                )
                return rsp['output']['choices'][0]['message']['content'].strip()
            else:
                return "[不支持的模型]"
        except Exception as e:
            error_msg = str(e)
            # 提供更详细的错误诊断
            if "404" in error_msg:
                if model == "Deepseek":
                    return f"[AI失败:Deepseek API配置错误，请检查API Key和模型名称。错误详情: {error_msg}]"
                elif model == "OpenAI":
                    return f"[AI失败:OpenAI API配置错误，请检查API Key。错误详情: {error_msg}]"
                elif model == "阿里千问":
                    return f"[AI失败:阿里千问API配置错误，请检查API Key。错误详情: {error_msg}]"
            elif "401" in error_msg:
                return f"[AI失败:API Key无效，请检查API Key是否正确。错误详情: {error_msg}]"
            elif "429" in error_msg:
                return f"[AI失败:API调用频率过高，请稍后重试。错误详情: {error_msg}]"
            elif "timeout" in error_msg.lower():
                return f"[AI失败:请求超时，请检查网络连接。错误详情: {error_msg}]"
            else:
                return f"[AI失败:{error_msg}]"
            
            if attempt < max_retries - 1:
                time.sleep(2)
                continue 

# ========== 内存缓存系统（适用于网页部署） ==========
import threading
from collections import OrderedDict
import time

class MemoryCache:
    """内存缓存系统，适用于网页部署环境"""
    
    def __init__(self, max_size=1000, ttl_hours=24):
        self.max_size = max_size
        self.ttl_seconds = ttl_hours * 3600
        self.cache = OrderedDict()
        self.lock = threading.Lock()
    
    def get(self, key):
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                # 检查是否过期
                if time.time() - timestamp < self.ttl_seconds:
                    # 更新访问顺序
                    self.cache.move_to_end(key)
                    return value
                else:
                    # 删除过期项
                    del self.cache[key]
        return None
    
    def set(self, key, value):
        """设置缓存值"""
        with self.lock:
            # 如果缓存已满，删除最旧的项
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            self.cache[key] = (value, time.time())
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self):
        """获取缓存统计"""
        with self.lock:
            current_time = time.time()
            valid_items = 0
            expired_items = 0
            
            for key, (value, timestamp) in self.cache.items():
                if current_time - timestamp < self.ttl_seconds:
                    valid_items += 1
                else:
                    expired_items += 1
            
            return {
                'total_items': len(self.cache),
                'valid_items': valid_items,
                'expired_items': expired_items,
                'max_size': self.max_size,
                'ttl_hours': self.ttl_seconds / 3600
            }

# 全局内存缓存实例
memory_cache = MemoryCache(max_size=2000, ttl_hours=24)

def get_memory_cache_key(text, engine, source='en', target='zh'):
    """生成内存缓存键"""
    content = f"{text}_{engine}_{source}_{target}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def save_to_memory_cache(cache_key, translation):
    """保存翻译结果到内存缓存"""
    memory_cache.set(cache_key, translation)

def load_from_memory_cache(cache_key):
    """从内存缓存加载翻译结果"""
    return memory_cache.get(cache_key)

def get_memory_cache_stats():
    """获取内存缓存统计"""
    return memory_cache.get_stats()

def clear_memory_cache():
    """清空内存缓存"""
    memory_cache.clear() 
