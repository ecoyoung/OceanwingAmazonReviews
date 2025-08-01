import streamlit as st
import pandas as pd
from utils import get_ai_cache_key, load_ai_label_from_cache, save_ai_label_to_cache, call_ai_model, get_download_data

st.set_page_config(
    page_title="Amazon评论分析 - AI批量标注",
    page_icon="🤖",
    layout="wide"
)

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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🤖 Amazon评论分析 - AI批量标注</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">基于AI的评论批量标签/结论生成工具</div>', unsafe_allow_html=True)

# 侧边栏：AI模型和API配置（始终显示）
with st.sidebar:
    st.markdown("### 🤖 AI模型配置")
    st.markdown("---")
    
    ai_model = st.selectbox("选择AI模型", ["OpenAI", "Deepseek", "阿里千问"])
    api_key = st.text_input("输入API Key", type="password")
    max_workers = st.slider("并发线程数", min_value=1, max_value=10, value=3, help="建议2-5，过高可能被API限流")
    
    # API测试功能
    if st.button("🧪 测试API连接", help="测试API Key是否有效", use_container_width=True):
        if not api_key:
            st.error("请先输入API Key")
        else:
            import requests
            # 先测试网络连接
            try:
                if ai_model == "Deepseek":
                    test_url = "https://api.deepseek.com/v1/models"
                elif ai_model == "OpenAI":
                    test_url = "https://api.openai.com/v1/models"
                else:
                    test_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
                response = requests.get(test_url, timeout=5)
                st.info(f"✅ 网络连接正常 (状态码: {response.status_code})")
            except Exception as e:
                st.warning(f"⚠️ 网络连接可能有问题: {str(e)}")
            # 测试AI API
            test_result = call_ai_model("测试", "请回复'测试成功'", ai_model, api_key)
            if "测试成功" in test_result:
                st.success("✅ API连接测试成功！")
            else:
                st.error(f"❌ API连接测试失败: {test_result}")
    
    # API配置提示
    st.markdown("""
    <div style='background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 0.5rem; font-size: 0.8rem;'>
    <strong>💡 API配置提示：</strong><br>
    • OpenAI: 使用OpenAI官方API Key<br>
    • Deepseek: 使用Deepseek API Key<br>
    • 阿里千问: 使用阿里云API Key
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 处理统计")
    st.markdown("---")
    
    # 显示当前状态
    if 'ai_settings' in st.session_state:
        task_count = len(st.session_state['ai_settings'])
        st.markdown(f"**当前任务数:** {task_count}")
    else:
        st.markdown("**当前任务数:** 0")
    
    if 'df' in locals():
        st.markdown(f"**数据量:** {len(df)} 条")
    else:
        st.markdown("**数据量:** 未上传")
    
    # 显示API状态
    if api_key:
        st.markdown("**API状态:** ✅ 已配置")
    else:
        st.markdown("**API状态:** ⚠️ 未配置")
    
    st.markdown("### 🚀 快速开始")
    st.markdown("---")
    st.markdown("""
    1. **配置API** - 选择模型并输入API Key
    2. **上传文件** - 选择Excel文件
    3. **设置任务** - 配置AI分析任务
    4. **开始标注** - 点击批量AI标注
    """)

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
        st.dataframe(df, use_container_width=True)

        # ========== AI批量标注功能 ========== #
        st.markdown("### 🤖 AI批量标签/结论生成")
        
        # 初始化AI设置
        if 'ai_settings' not in st.session_state:
            st.session_state['ai_settings'] = [
                {
                    "name": "AI任务1",
                    "col_name": "产品功效",
                    "prompt": "请根据{Content}列的内容，总结消费者购买产品是为了产品的什么功效？按照如下格式：功效1 | 功效2 | 功效3 | ...",
                    "source_col": "Content"
                }
            ]
        
        ai_settings = st.session_state['ai_settings']
        
        # AI任务设置
        st.markdown("#### 📝 AI任务设置")
        
        # 显示所有AI任务
        for i, setting in enumerate(ai_settings):
            with st.expander(f"🤖 {setting['name']}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    setting['name'] = st.text_input("任务名称", value=setting['name'], key=f"task_name_{i}")
                    setting['col_name'] = st.text_input("新列名", value=setting['col_name'], key=f"col_name_{i}")
                with col2:
                    setting['source_col'] = st.selectbox("数据源列", df.columns, index=df.columns.get_loc(setting['source_col']) if setting['source_col'] in df.columns else 0, key=f"source_col_{i}")
                
                setting['prompt'] = st.text_area("AI提问模板", value=setting['prompt'], height=100, key=f"prompt_{i}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🗑️ 删除任务", key=f"delete_task_{i}"):
                        ai_settings.pop(i)
                        st.session_state['ai_settings'] = ai_settings
                        st.rerun()
                with col2:
                    st.markdown(f"**预览：** 将生成列 '{setting['col_name']}' 基于 '{setting['source_col']}' 列")
        
        # 添加新任务按钮
        if st.button("➕ 新增AI任务", use_container_width=True):
            new_task = {
                "name": f"AI任务{len(ai_settings)+1}",
                "col_name": f"AI标签{len(ai_settings)+1}",
                "prompt": "请分析以下内容：{Content}",
                "source_col": "Content"
            }
            ai_settings.append(new_task)
            st.session_state['ai_settings'] = ai_settings
            st.rerun()
        
        # 批量执行AI标注
        if st.button("🚀 批量AI标注", type="primary", use_container_width=True):
            if not api_key:
                st.error("请填写API Key")
            elif not ai_settings:
                st.error("请至少添加一个AI任务")
            else:
                from concurrent.futures import ThreadPoolExecutor, as_completed
                import time
                
                progress = st.progress(0)
                status = st.empty()
                df_result = df.copy()
                
                total_tasks = len(df) * len(ai_settings)
                task_count = 0
                
                def ai_label_worker(row, prompt_template, source_col, ai_model, api_key):
                    try:
                        # 构建包含所有列数据的字典
                        row_data = {col: str(row[col]) for col in df.columns}
                        # 格式化提示词
                        try:
                            if "{Content}" in prompt_template:
                                formatted_prompt = prompt_template.format(Content=str(row[source_col]))
                            elif "{text}" in prompt_template:
                                formatted_prompt = prompt_template.format(text=str(row[source_col]))
                            else:
                                formatted_prompt = prompt_template
                        except Exception:
                            formatted_prompt = prompt_template
                        
                        # 使用源列内容作为主要文本
                        text_content = str(row[source_col])
                        
                        cache_key = get_ai_cache_key(text_content, formatted_prompt, ai_model)
                        label = load_ai_label_from_cache(cache_key)
                        if label is None:
                            label = call_ai_model(text_content, formatted_prompt, ai_model, api_key)
                            save_ai_label_to_cache(cache_key, label)
                        return label
                    except Exception as e:
                        return f"[AI异常: {str(e)[:30]}]"
                
                # 为每个AI任务处理数据
                for setting_idx, setting in enumerate(ai_settings):
                    col_name = setting["col_name"]
                    prompt_template = setting["prompt"]
                    source_col = setting["source_col"]
                    
                    status.info(f"正在处理任务 '{setting['name']}' ({setting_idx+1}/{len(ai_settings)})")
                    
                    ai_labels = [None] * len(df)
                    
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures = {
                            executor.submit(ai_label_worker, row, prompt_template, source_col, ai_model, api_key): idx
                            for idx, (_, row) in enumerate(df.iterrows())
                        }
                        
                        for i, future in enumerate(as_completed(futures)):
                            idx = futures[future]
                            try:
                                ai_labels[idx] = future.result()
                            except Exception as e:
                                ai_labels[idx] = f"[AI异常: {str(e)[:30]}]"
                            
                            task_count += 1
                            progress.progress(task_count / total_tasks)
                            status.info(f"任务 '{setting['name']}' 已处理 {i+1}/{len(df)} | 总进度 {task_count}/{total_tasks}")
                    
                    df_result[col_name] = ai_labels
                
                st.success("✅ AI批量标注完成！")
                st.dataframe(df_result, use_container_width=True)
                st.download_button(
                    label="📥 下载带AI标签的表格",
                    data=get_download_data(df_result, 'excel'),
                    file_name="ai_labeled_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    except Exception as e:
        st.error(f"❌ 处理文件时出错: {str(e)}")
else:
    st.info("👆 请上传包含ID、Content和Review Type列的Excel文件。上传后可进行AI批量标签/结论生成。") 