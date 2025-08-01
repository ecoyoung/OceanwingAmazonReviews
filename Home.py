import streamlit as st
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import plotly.figure_factory as ff
from utils import process_data, get_download_data, calculate_review_stats, create_pie_chart, analyze_by_group, create_rating_trend_chart, create_rating_heatmap, save_fig_to_html
import base64

# 应用配置 - 可以在这里修改logo和作者信息
APP_CONFIG = {
    "app_title": "Amazon Review Analytics Pro",
    "app_subtitle": "专业的亚马逊评论数据分析平台",
    "author": "海翼IDC团队",
    "version": "v1.5.0",
    "最近更新时间": "2025-08-01",
    "contact": "idc@oceanwing.com",
    # logo_path 可以设置为本地图片路径，或者使用base64编码的图片
    "logo_path": None,  # 设置为IDClogo图片文件路径，如 "logo.png"
    "company": "Anker Oceanwing Inc."
}

def get_base64_image(image_path):
    """将图片转换为base64编码"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def display_header():
    """显示页面头部信息"""
    # 自定义CSS样式
    st.markdown("""
    <style>
    /* 主要样式 */
    .main-header {
        background: linear-gradient(135deg, #FF9500 0%, #FF6B35 50%, #232F3E 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(255, 149, 0, 0.3);
    }
    
    .app-title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .app-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .author-info {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* 橙色风格的卡片 */
    .amazon-card {
        background: white;
        border: 1px solid #DDD;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .amazon-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #FF9500;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .stats-container {
        background: linear-gradient(135deg, #232F3E 0%, #37475A 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .upload-area {
        border: 2px dashed #FF9500;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: rgba(255, 149, 0, 0.05);
        transition: all 0.3s;
    }
    
    .upload-area:hover {
        border-color: #FF6B35;
        background: rgba(255, 149, 0, 0.1);
    }
    
    .success-message {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .app-title {
            font-size: 2rem;
        }
        
        .app-subtitle {
            font-size: 1rem;
        }
        
        .main-header {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 显示头部信息
    header_html = f"""
    <div class="main-header">
        <div class="app-title">{APP_CONFIG['app_title']}</div>
        <div class="app-subtitle">{APP_CONFIG['app_subtitle']}</div>
        <div class="author-info">
            <strong>开发团队:</strong> {APP_CONFIG['author']} 
               <strong></strong> {APP_CONFIG['contact']} | 
            <strong>版本:</strong> {APP_CONFIG['version']} | 
              <strong>最近更新时间:</strong> {APP_CONFIG['最近更新时间']} | 
            <strong>公司:</strong> {APP_CONFIG['company']}
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def display_features():
    """显示功能特性"""
    st.markdown("""
    <div class="feature-card">
        <h3>🚀 核心功能</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #4CAF50;">
                <h4>📊 数据预处理</h4>
                <p>自动清洗和标准化Amazon评论数据，支持多种数据格式</p>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196F3;">
                <h4>🌐 智能翻译</h4>
                <p>支持Google翻译和腾讯翻译API，智能缓存提升效率</p>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #FF9800;">
                <h4>📈 统计分析</h4>
                <p>全方位评论数据统计分析，包含情感分析和可视化</p>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #9C27B0;">
                <h4>🎯 关键词匹配</h4>
                <p>智能关键词匹配和人群分类，精准定位目标用户</p>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #E91E63;">
                <h4>🤖 AI标签</h4>
                <p>AI赋能的评论分析&标签分类</p>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #607D8B;">
                <h4>💾 智能缓存</h4>
                <p>自动缓存翻译和AI结果，避免重复处理，大幅提升效率</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_workflow():
    """显示工作流程"""
    st.markdown("""
    <div class="feature-card">
        <h3>📋 使用流程</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <h4>1️⃣ 数据上传</h4>
                <p>上传Excel格式的Amazon评论数据</p>
            </div>
            <div style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <h4>2️⃣ 数据预处理</h4>
                <p>自动清洗和标准化数据格式</p>
            </div>
            <div style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <h4>3️⃣ 评论翻译</h4>
                <p>批量翻译英文评论为中文</p>
            </div>
            <div style="background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <h4>4️⃣ 统计分析</h4>
                <p>生成可视化图表和统计报告</p>
            </div>
            <div style="background: linear-gradient(135deg, #E91E63 0%, #C2185B 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <h4>5️⃣ 关键词匹配</h4>
                <p>基于关键词进行人群分类</p>
            </div>
            <div style="background: linear-gradient(135deg, #607D8B 0%, #455A64 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <h4>6️⃣ 报告生成</h4>
                <p>导出分析结果和可视化报告</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def process_uploaded_file(uploaded_file):
    """处理上传的文件"""
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            st.error("不支持的文件格式，请上传Excel(.xlsx)或CSV文件")
            return None
        
        st.success(f"✅ 文件上传成功！共读取 {len(df)} 条记录")
        return df
    except Exception as e:
        st.error(f"❌ 文件读取失败: {str(e)}")
        return None

def process_brand_file(uploaded_file):
    """处理品牌文件"""
    try:
        if uploaded_file.name.endswith('.xlsx'):
            brand_df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            brand_df = pd.read_csv(uploaded_file)
        else:
            st.error("不支持的文件格式，请上传Excel(.xlsx)或CSV文件")
            return None
        
        # 检查必要的列
        required_columns = ['ASIN', 'Brand']
        if not all(col in brand_df.columns for col in required_columns):
            st.error(f"品牌文件缺少必要的列: {[col for col in required_columns if col not in brand_df.columns]}")
            return None
        
        # 检查是否有Parent ASIN列
        has_parent_asin = 'Parent ASIN' in brand_df.columns
        
        st.success(f"✅ 品牌文件上传成功！共读取 {len(brand_df)} 条记录")
        if has_parent_asin:
            st.info("📋 检测到Parent ASIN列，将启用双重连接逻辑")
        else:
            st.warning("⚠️ 未检测到Parent ASIN列，将仅使用ASIN连接")
        
        return brand_df
    except Exception as e:
        st.error(f"❌ 品牌文件读取失败: {str(e)}")
        return None

def main():
    """主函数"""
    # 页面配置
    st.set_page_config(
        page_title=APP_CONFIG['app_title'],
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 显示头部
    display_header()
    
    # 显示功能特性
    display_features()
    
    # 显示工作流程
    display_workflow()
    
    # 文件上传区域
    st.markdown("""
    <div class="upload-area">
        <h3>📁 数据上传</h3>
        <p>请上传Amazon评论数据文件（Excel或CSV格式）</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择评论数据文件",
        type=['xlsx', 'csv'],
        help="支持Excel(.xlsx)和CSV格式文件"
    )
    
    # 品牌文件上传
    brand_file = st.file_uploader(
        "选择品牌数据文件（可选）",
        type=['xlsx', 'csv'],
        help="包含ASIN、Brand和Parent ASIN列的文件，用于关联品牌信息。系统会先尝试ASIN匹配，未匹配的再用Parent ASIN匹配。"
    )
    
    if uploaded_file is not None:
        # 处理上传的文件
        df = process_uploaded_file(uploaded_file)
        
        if df is not None:
            # 处理品牌文件
            brand_df = None
            if brand_file is not None:
                brand_df = process_brand_file(brand_file)
            
            # 数据预处理
            processed_df = process_data(df, brand_df)
            
            if processed_df is not None:
                # 显示数据统计
                st.markdown("""
                <div class="stats-container">
                    <h3>📊 数据概览</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # 计算统计信息
                stats = calculate_review_stats(processed_df)
                
                # 显示统计信息
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("总评论数", len(processed_df))
                
                with col2:
                    st.metric("平均评分", f"{processed_df['Rating'].mean():.2f}")
                
                with col3:
                    positive_count = len(processed_df[processed_df['Review Type'] == 'positive'])
                    st.metric("正面评论", positive_count)
                
                with col4:
                    negative_count = len(processed_df[processed_df['Review Type'] == 'negative'])
                    st.metric("负面评论", negative_count)
                
                # 显示评论类型分布
                review_counts = processed_df['Review Type'].value_counts()
                fig = create_pie_chart(review_counts)
                st.plotly_chart(fig, use_container_width=True)
                
                # 保存处理后的数据到session state
                st.session_state['processed_data'] = processed_df
                st.session_state['original_data'] = df
                
                st.success("✅ 数据处理完成！请使用左侧菜单进行进一步分析。")
                
                # 显示数据预览
                with st.expander("📋 数据预览"):
                    st.dataframe(processed_df.head(10), use_container_width=True)
                    
                    # 下载处理后的数据
                    download_data = get_download_data(processed_df)
                    st.download_button(
                        label="📥 下载处理后的数据",
                        data=download_data,
                        file_name=f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

if __name__ == "__main__":
    main()