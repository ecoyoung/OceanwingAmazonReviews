import streamlit as st
import re

# ========== 如需使用 Deepseek，必须 pip install --upgrade openai 至 1.x 版本 ==========
from utils import get_download_data

# 设置页面配置必须是第一个st命令
st.set_page_config(
    page_title="Amazon评论分析 - 关键词匹配",
    page_icon="🔍",
    layout="wide"
)

import pandas as pd
import json
import os
from collections import defaultdict
import plotly.graph_objects as go

# 预设人群类别和关键词
PRESET_CATEGORIES = {
    "人群画像": {
        "儿童或青少年": "kids,girl,girls,boy,boys,children,teen,picky eater,child-friendly,baby,sugar coating,candy-like,my daughter,my son",
        "孕妇或哺乳期女性": "pregnant,pregnancy,nursing,breastfeeding,menstrual,period,hormonal support,prenatal,postpartum,label says do not use during pregnancy",
        "素食者或健康饮食者": "vegan,vegetarian,plant-based,no artificial,no gluten,no high fructose corn syrup,organic,non-GMO,natural ingredients,sugar-free,low sugar,stevia",
        "健身运动人群": "fitness,exercise,training,athlete,workout,gym,sports,muscle,strength,endurance,protein,Boosts endurance,Boosts strength"
    },
    "购买动机": {
        "消化系统健康": "digestive, gut, bloating, fiber, strains,GI"
    },
    "用户痛点": {
        "产品效果痛点": "ineffective,not effective,doesn't work,no results,didn't notice any change,no effect,no improvement,didn't help,weak effect,didn't feel anything,too mild,lack of results,unnoticeable change,not strong enough",
        "健康改善痛点": "still tired,no energy,constantly sick,weak immune system,didn't boost energy,low stamina,fatigue persists,feel drained,didn't help recovery,always exhausted,immunity not improved,keeps getting sick",
        "口感与体验痛点": "bad taste,terrible flavor,unpleasant aftertaste,tastes bad,too bitter,tastes like medicine,chemical taste,weird smell,chalky,grainy,hard to swallow,too sweet,artificial taste,nauseating flavor",
        "症状缓解痛点": "cough didn't go away,still congested,no relief,breathing issues remain,didn't ease symptoms,no change in cough,mucus still there,asthma got worse,sinuses still blocked,chest still tight,didn't help with colds",
        "包装与便利性痛点": "too small,not enough doses,bottle leaks,poorly designed packaging,hard to open,messy to use,inconvenient size,not portable,dosage unclear,ran out quickly,frequent repurchase,short supply,not user-friendly",
        "天然与安全性痛点": "contains chemicals,artificial ingredients,synthetic fillers,caused reaction,allergic response,unsafe formula,questionable ingredients,not natural,GMO concern,unclear label,hidden additives,harsh ingredients",
        "消费者体验与反馈痛点": "bad reviews,low rating,not recommended,disappointed,didn't meet expectations,poor experience,wouldn't buy again,waste of money,overhyped,felt scammed,not as described,unreliable product,inconsistent results"
    }
}

def load_categories():
    """从文件加载已保存的类别和关键词"""
    if os.path.exists('config/categories.json'):
        with open('config/categories.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 处理旧格式的数据
            if isinstance(data, dict) and all(isinstance(v, str) for v in data.values()):
                # 将旧格式转换为新格式
                new_data = {
                    "人群画像": {},
                    "购买动机": {},
                    "用户痛点": {}
                }
                for category, keywords in data.items():
                    if category in PRESET_CATEGORIES["人群画像"]:
                        new_data["人群画像"][category] = keywords
                    elif category in PRESET_CATEGORIES["购买动机"]:
                        new_data["购买动机"][category] = keywords
                    else:
                        new_data["用户痛点"][category] = keywords
                return new_data
            return data
    return {"人群画像": {}, "购买动机": {}, "用户痛点": {}}

def save_categories(categories):
    """保存类别和关键词到文件"""
    with open('config/categories.json', 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

def process_keywords(keywords_text):
    """处理关键词文本"""
    if not keywords_text:
        return []
    
    # 使用更高效的文本处理
    keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]
    # 使用集合去重
    return list(set(keywords))

def find_matches(text, keywords):
    """查找文本中的关键词匹配"""
    if pd.isna(text) or not text:
        return []
    
    text = str(text).lower()
    # 使用集合操作提高效率
    return [k for k in keywords if k.lower() in text]

def analyze_keyword_matches(df, keywords):
    """分析关键词匹配"""
    # 使用向量化操作处理文本，避免apply
    text_series = df['Content'].astype(str).str.lower()
    matches_list = []
    
    for text in text_series:
        matches = [k for k in keywords if k.lower() in text]
        matches_list.append(matches)
    
    df['Matches'] = matches_list
    df['Match_Count'] = df['Matches'].str.len()
    
    # 计算匹配统计
    total_reviews = len(df)
    matched_reviews = (df['Match_Count'] > 0).sum()
    match_rate = matched_reviews / total_reviews * 100
    
    # 使用更高效的分组统计
    rating_stats = df[df['Match_Count'] > 0].groupby('Rating')['Match_Count'].agg(['count', 'mean']).round(2)
    rating_stats.columns = ['评论数', '平均匹配数']
    
    return {
        'total_reviews': total_reviews,
        'matched_reviews': matched_reviews,
        'match_rate': match_rate,
        'rating_stats': rating_stats
    }

def create_match_visualization(df, keywords):
    """创建匹配可视化"""
    # 使用更高效的数据处理
    match_data = df[df['Match_Count'] > 0].copy()
    
    # 创建匹配词云
    word_freq = {}
    for matches in match_data['Matches']:
        for word in matches:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # 使用更高效的图表创建
    fig = go.Figure()
    
    # 添加匹配分布
    fig.add_trace(go.Bar(
        x=match_data['Rating'].value_counts().index,
        y=match_data['Rating'].value_counts().values,
        name='匹配评论数',
        marker_color='#2E86AB'
    ))
    
    fig.update_layout(
        title='关键词匹配分布',
        xaxis_title='评分',
        yaxis_title='评论数',
        showlegend=True,
        template='plotly_white'
    )
    
    return fig, word_freq

def analyze_reviews(df, categories):
    """分析评论并进行分类"""
    # 创建结果DataFrame，保留ID列
    results = pd.DataFrame()
    results['ID'] = df['ID']  # 保留原始ID
    results['Content'] = df['Content']
    results['Original Review Type'] = df['Review Type']

    # 检查并保留翻译内容列
    translation_col_candidates = ['Content_zh', '翻译内容', 'Translation', 'content_zh', 'translated_content']
    for col in translation_col_candidates:
        if col in df.columns:
            results[col] = df[col]
            break  # 只保留第一个检测到的翻译列

    # 预处理文本数据，提高性能
    text_series = df['Content'].astype(str).str.lower()
    
    # 为每个类别创建一列（列名为"是否{main_category}-{sub_category}"）
    for main_category, sub_categories in categories.items():
        if isinstance(sub_categories, dict):  # 新格式
            for sub_category, keywords in sub_categories.items():
                # 将关键词字符串转换为列表
                keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
                
                # 使用向量化操作替代apply
                matches = []
                for text in text_series:
                    has_match = any(k.lower() in text for k in keyword_list)
                    matches.append(has_match)
                
                results[f'是否{main_category}-{sub_category}'] = matches
        else:  # 旧格式
            # 将关键词字符串转换为列表
            keyword_list = [k.strip() for k in sub_categories.split(',') if k.strip()]
            
            # 使用向量化操作替代apply
            matches = []
            for text in text_series:
                has_match = any(k.lower() in text for k in keyword_list)
                matches.append(has_match)
            
            results[f'是否{main_category}'] = matches

    # 统计每个类别的匹配数量
    stats = {}
    for main_category, sub_categories in categories.items():
        stats[main_category] = {}
        if isinstance(sub_categories, dict):  # 新格式
            for sub_category in sub_categories:
                matched = results[f'是否{main_category}-{sub_category}'].sum()
                stats[main_category][sub_category] = {
                    'matched': int(matched),
                    'percentage': round(matched / len(df) * 100, 2)
                }
        else:  # 旧格式
            matched = results[f'是否{main_category}'].sum()
            stats[main_category] = {
                'matched': int(matched),
                'percentage': round(matched / len(df) * 100, 2)
            }

    return results, stats

def analyze_keyword_frequency(df, categories):
    """分析每个类别的关键词匹配频率"""
    keyword_stats = {}
    
    for main_category, sub_categories in categories.items():
        keyword_stats[main_category] = {}
        if isinstance(sub_categories, dict):  # 新格式
            for sub_category, keywords in sub_categories.items():
                # 将关键词字符串转换为列表
                keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
                # 统计每个关键词的匹配次数
                keyword_freq = defaultdict(int)
                for content in df['Content']:
                    matches = find_matches(content, keyword_list)
                    for match in matches:
                        keyword_freq[match] += 1
                
                # 转换为DataFrame并排序
                if keyword_freq:
                    freq_df = pd.DataFrame({
                        '关键词': list(keyword_freq.keys()),
                        '匹配次数': list(keyword_freq.values())
                    })
                    freq_df = freq_df.sort_values('匹配次数', ascending=False)
                    keyword_stats[main_category][sub_category] = freq_df
                else:
                    keyword_stats[main_category][sub_category] = pd.DataFrame(columns=['关键词', '匹配次数'])
    
    return keyword_stats

def main():
    # 页面标题和样式
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5em;
        margin-bottom: 0.5em;
        font-weight: bold;
    }
    .sub-header {
        text-align: center;
        color: #A23B72;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .category-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .preset-category {
        background-color: #e7f3ff;
        border-left: 4px solid #2E86AB;
    }
    .stats-card {
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">🔍 Amazon评论分析 - 关键词匹配</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">基于关键词匹配的评论分类分析工具</div>', unsafe_allow_html=True)
    
    # 加载已保存的类别
    categories = load_categories()
    
    # 侧边栏：预设类别快速导入
    with st.sidebar:
        st.markdown("### 🎯 预设类别")
        st.markdown("---")
        
        for main_category, sub_categories in PRESET_CATEGORIES.items():
            st.markdown(f"#### {main_category}")
            for sub_category, keywords in sub_categories.items():
                with st.container():
                    st.markdown(f"**{sub_category}**")
                    
                    # 显示关键词预览
                    preview_keywords = keywords.split(',')[:5]
                    preview_text = ', '.join(preview_keywords)
                    if len(keywords.split(',')) > 5:
                        preview_text += f"... (共{len(keywords.split(','))}个关键词)"
                    
                    st.markdown(f"<small style='color: #666;'>{preview_text}</small>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"一键导入", key=f"import_{main_category}_{sub_category}"):
                            if main_category not in categories:
                                categories[main_category] = {}
                            categories[main_category][sub_category] = keywords
                            save_categories(categories)
                            st.success("导入成功！")
                            st.rerun()
                    
                    with col2:
                        if main_category in categories and sub_category in categories[main_category]:
                            st.markdown("✅ 已导入")
                        else:
                            st.markdown("⭕ 未导入")
                    
                    st.markdown("---")
        
        # ========== 自定义类别管理 ========== #
        st.markdown("### 🛠️ 自定义类别管理")
        st.markdown("---")
        
        # 新增主类别
        with st.expander("➕ 新增主类别", expanded=False):
            new_main_category = st.text_input("主类别名称", key="new_main_category")
            if st.button("添加主类别", key="add_main_category"):
                if new_main_category.strip():
                    if new_main_category not in categories:
                        categories[new_main_category] = {}
                        save_categories(categories)
                        st.success(f"主类别 '{new_main_category}' 已添加！")
                        st.rerun()
                    else:
                        st.warning("主类别已存在！")
                else:
                    st.warning("主类别名称不能为空！")
        
        # 显示所有类别（包括自定义的）
        st.markdown("#### 📋 当前所有类别")
        
        for main_category in list(categories.keys()):
            st.markdown(f"**🗂️ {main_category}**")
            
            # 删除主类别按钮
            if st.button(f"❌ 删除主类别", key=f"del_main_{main_category}"):
                del categories[main_category]
                save_categories(categories)
                st.success(f"主类别 '{main_category}' 已删除！")
                st.rerun()
            
            # 为每个主类别添加子类别
            with st.expander(f"➕ 为 {main_category} 添加子类别", expanded=False):
                new_sub_category = st.text_input("子类别名称", key=f"new_sub_{main_category}")
                new_keywords = st.text_area("关键词（逗号分隔）", key=f"new_keywords_{main_category}")
                if st.button("添加子类别", key=f"add_sub_{main_category}"):
                    if new_sub_category.strip():
                        if new_sub_category not in categories[main_category]:
                            categories[main_category][new_sub_category] = new_keywords
                            save_categories(categories)
                            st.success(f"子类别 '{new_sub_category}' 已添加！")
                            st.rerun()
                        else:
                            st.warning("子类别已存在！")
                    else:
                        st.warning("子类别名称不能为空！")
            
            # 显示该主类别下的所有子类别
            for sub_category in list(categories[main_category].keys()):
                st.markdown(f"**└─ {sub_category}**")
                
                # 编辑关键词
                current_keywords = categories[main_category][sub_category]
                edited_keywords = st.text_area(
                    f"编辑关键词（逗号分隔）", 
                    value=current_keywords,
                    key=f"edit_keywords_{main_category}_{sub_category}",
                    height=100
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 保存", key=f"save_{main_category}_{sub_category}"):
                        categories[main_category][sub_category] = edited_keywords
                        save_categories(categories)
                        st.success("关键词已保存！")
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ 删除子类别", key=f"del_sub_{main_category}_{sub_category}"):
                        del categories[main_category][sub_category]
                        save_categories(categories)
                        st.success(f"子类别 '{sub_category}' 已删除！")
                        st.rerun()
                
                st.markdown("---")
        
        # 如果有分析结果，显示匹配统计
        if 'stats' in locals() and stats:
            st.markdown("### 📊 匹配统计概览")
            st.markdown("---")
            
            # 创建简化的统计显示
            top_stats = []
            for main_category, sub_categories in stats.items():
                for sub_category, stat in sub_categories.items():
                    top_stats.append({
                        'category': f"{main_category} - {sub_category}",
                        'percentage': stat['percentage'],
                        'matched': stat['matched']
                    })
            
            # 按匹配比例排序，只显示前5个
            top_stats.sort(key=lambda x: x['percentage'], reverse=True)
            top_stats = top_stats[:5]
            
            for i, stat in enumerate(top_stats):
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 5px; margin: 0.2rem 0;">
                    <strong style="color: #2E86AB;">{i+1}. {stat['category']}</strong><br>
                    <span style="color: #A23B72; font-size: 0.9rem;">{stat['percentage']}% ({stat['matched']}条)</span>
                </div>
                """, unsafe_allow_html=True)
    
    # ========== 主体内容区域 ========== #
    # 判断是否有类别
    has_categories = bool(categories and any(len(sub) > 0 for sub in categories.values()))

    # 文件上传控件，始终可见
    uploaded_file = st.file_uploader(
        "选择预处理后的Excel文件", 
        type=['xlsx'],
        help="请上传包含ID、Content和Review Type列的Excel文件"
    )
    if uploaded_file is not None:
        try:
            with st.spinner('正在处理文件...'):
                df = pd.read_excel(uploaded_file)
            st.success(f"✅ 文件上传成功！共 {len(df)} 条评论")
            st.markdown("""
            <div style='background: #e3f2fd; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.2rem; box-shadow: 0 2px 8px rgba(33,150,243,0.08);'>
                <h4 style='color: #1976d2; margin: 0;'>📝 原始评论表格</h4>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)

            # 如果有类别，显示原有分析流程
            if has_categories:
                # 分析评论
                with st.spinner('正在分析评论...'):
                    results, stats = analyze_reviews(df, categories)
                
                # 显示统计信息
                st.markdown("### 📈 匹配统计结果")
                
                # 添加排序选项
                col1, col2 = st.columns(2)
                with col1:
                    sort_by = st.selectbox(
                        "排序方式",
                        ["匹配比例", "匹配数量", "类别名称"],
                        help="选择统计结果的排序方式"
                    )
                
                with col2:
                    sort_order = st.selectbox(
                        "排序顺序",
                        ["降序", "升序"],
                        help="选择排序顺序"
                    )
                
                # 创建美观的统计卡片，按选择的排序方式排列
                all_stats = []
                for main_category, sub_categories in stats.items():
                    for sub_category, stat in sub_categories.items():
                        all_stats.append({
                            'main_category': main_category,
                            'sub_category': sub_category,
                            'category': f"{main_category} - {sub_category}",
                            'matched': stat['matched'],
                            'percentage': stat['percentage']
                        })
                
                # 根据选择的排序方式排序
                if sort_by == "匹配比例":
                    all_stats.sort(key=lambda x: x['percentage'], reverse=(sort_order == "降序"))
                elif sort_by == "匹配数量":
                    all_stats.sort(key=lambda x: x['matched'], reverse=(sort_order == "降序"))
                else:  # 类别名称
                    all_stats.sort(key=lambda x: x['category'], reverse=(sort_order == "降序"))
                
                # 每行显示4个统计卡片
                cols = st.columns(min(len(all_stats), 4))
                for i, stat in enumerate(all_stats):
                    with cols[i % 4]:
                        st.markdown(f"""
                        <div class="stats-card">
                            <h4 style="color: #2E86AB; margin: 0;">{stat['category']}</h4>
                            <h2 style="color: #A23B72; margin: 0.5rem 0;">{stat['matched']}</h2>
                            <p style="color: #666; margin: 0;">匹配率: {stat['percentage']}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 详细统计表格，按选择的排序方式排列
                stats_df = pd.DataFrame([
                    {
                        '主类别': main_category,
                        '子类别': sub_category,
                        '匹配数量': stats[main_category][sub_category]['matched'],
                        '匹配比例': stats[main_category][sub_category]['percentage'],
                        '匹配比例(%)': f"{stats[main_category][sub_category]['percentage']}%",
                        '未匹配数量': len(df) - stats[main_category][sub_category]['matched']
                    }
                    for main_category in stats
                    for sub_category in stats[main_category]
                ])
                
                # 根据选择的排序方式排序
                if sort_by == "匹配比例":
                    stats_df = stats_df.sort_values('匹配比例', ascending=(sort_order == "升序"))
                elif sort_by == "匹配数量":
                    stats_df = stats_df.sort_values('匹配数量', ascending=(sort_order == "升序"))
                else:  # 类别名称
                    stats_df = stats_df.sort_values(['主类别', '子类别'], ascending=(sort_order == "升序"))
                
                st.markdown(f"#### 📋 详细统计表")
                st.dataframe(stats_df[['主类别', '子类别', '匹配数量', '匹配比例(%)', '未匹配数量']], use_container_width=True)
                
                # 显示详细结果
                st.markdown("### 📄 详细分析结果")
                
                # 添加关键词匹配统计
                st.markdown("### 🔍 关键词匹配统计")
                keyword_freq_stats = analyze_keyword_frequency(df, categories)
                
                # 添加排序选项
                col1, col2 = st.columns(2)
                with col1:
                    keyword_sort_by = st.selectbox(
                        "关键词统计排序方式",
                        ["匹配比例", "匹配数量", "类别名称"],
                        help="选择关键词统计的排序方式",
                        key="keyword_sort"
                    )
                
                with col2:
                    keyword_sort_order = st.selectbox(
                        "关键词统计排序顺序",
                        ["降序", "升序"],
                        help="选择关键词统计的排序顺序",
                        key="keyword_sort_order"
                    )
                
                # 为每个类别创建选项卡
                tabs = st.tabs(list(keyword_freq_stats.keys()) if len(keyword_freq_stats) > 0 else ["无类别"])
                for tab, main_category in zip(tabs, keyword_freq_stats.keys() if len(keyword_freq_stats) > 0 else [""]):
                    with tab:
                        st.markdown(f"#### {main_category}关键词匹配统计")
                        
                        # 获取该主类别下所有子类别的匹配统计，用于排序
                        category_stats = []
                        for sub_category in keyword_freq_stats[main_category].keys():
                            if sub_category in stats.get(main_category, {}):
                                category_stats.append({
                                    'sub_category': sub_category,
                                    'percentage': stats[main_category][sub_category]['percentage'],
                                    'matched': stats[main_category][sub_category]['matched']
                                })
                        
                        # 根据选择的排序方式排序子类别
                        if keyword_sort_by == "匹配比例":
                            category_stats.sort(key=lambda x: x['percentage'], reverse=(keyword_sort_order == "降序"))
                        elif keyword_sort_by == "匹配数量":
                            category_stats.sort(key=lambda x: x['matched'], reverse=(keyword_sort_order == "降序"))
                        else:  # 类别名称
                            category_stats.sort(key=lambda x: x['sub_category'], reverse=(keyword_sort_order == "降序"))
                        
                        for category_stat in category_stats:
                            sub_category = category_stat['sub_category']
                            freq_df = keyword_freq_stats[main_category][sub_category]
                            
                            if not freq_df.empty:
                                st.markdown(f"**{sub_category}** (匹配率: {category_stat['percentage']}%, 匹配数量: {category_stat['matched']})")
                                # 显示前10个最常匹配的关键词
                                top_keywords = freq_df.head(10)
                                
                                # 创建柱状图
                                fig = go.Figure(data=[
                                    go.Bar(
                                        x=top_keywords['关键词'],
                                        y=top_keywords['匹配次数'],
                                        marker_color='#2E86AB'
                                    )
                                ])
                                
                                fig.update_layout(
                                    title=f"{sub_category} - 关键词匹配频率",
                                    xaxis_title="关键词",
                                    yaxis_title="匹配次数",
                                    showlegend=False,
                                    height=400
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # 显示详细数据表格
                                with st.expander("查看完整数据"):
                                    st.dataframe(freq_df, use_container_width=True)
                            else:
                                st.info(f"{sub_category} 没有匹配的关键词")
                
                # 添加筛选选项
                col_count = 2
                col1, col2 = st.columns([1]*col_count)
                with col1:
                    show_all = st.checkbox("显示所有记录", value=True)
                
                with col2:
                    if not show_all:
                        # 创建类别选择列表，按选择的排序方式排列
                        category_options = []
                        for main_category in stats:
                            for sub_category in stats[main_category]:
                                category_options.append({
                                    'display': f"{main_category} - {sub_category}",
                                    'column': f"是否{main_category}-{sub_category}",
                                    'percentage': stats[main_category][sub_category]['percentage'],
                                    'matched': stats[main_category][sub_category]['matched']
                                })
                        
                        # 根据选择的排序方式排序
                        if sort_by == "匹配比例":
                            category_options.sort(key=lambda x: x['percentage'], reverse=(sort_order == "降序"))
                        elif sort_by == "匹配数量":
                            category_options.sort(key=lambda x: x['matched'], reverse=(sort_order == "降序"))
                        else:  # 类别名称
                            category_options.sort(key=lambda x: x['display'], reverse=(sort_order == "降序"))
                        
                        # 创建显示选项，包含匹配率信息
                        display_options = [f"{opt['display']} ({opt['percentage']}%, {opt['matched']}条)" for opt in category_options]
                        
                        selected_display = st.selectbox(
                            f"选择要查看的类别（按{sort_by}{sort_order}排序）",
                            options=display_options
                        )
                        
                        # 根据选择的显示选项找到对应的列名
                        selected_index = display_options.index(selected_display)
                        selected_category = category_options[selected_index]['column']
                
                # 根据筛选条件显示结果
                if show_all:
                    st.dataframe(results, use_container_width=True)
                else:
                    filtered_results = results[results[f'是否{selected_category}'] == True]
                    st.dataframe(filtered_results, use_container_width=True)
                    st.info(f"显示 {len(filtered_results)} 条匹配 '{selected_category}' 的记录")
                
                # 合并原始df和标签列
                label_cols = [col for col in results.columns if col.startswith('是否')]
                display_df = df.copy()
                for col in label_cols:
                    display_df[col] = results[col]
                st.markdown("### 📝 匹配后结果表格（含标签）")
                st.dataframe(display_df, use_container_width=True)

                # 保留原有的关键词匹配结果下载功能
                st.markdown("### 📥 下载匹配结果")
                st.download_button(
                    label="📥 下载匹配结果",
                    data=get_download_data(df, 'excel'),
                    file_name="keyword_match_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"❌ 处理文件时出错: {str(e)}")
    else:
        st.info("👆 请上传包含ID、Content和Review Type列的Excel文件。上传后可直接进行关键词匹配和统计。")

if __name__ == "__main__":
    main()