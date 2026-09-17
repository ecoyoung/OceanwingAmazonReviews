**English** | [简体中文](README.md)

# Amazon Review Analytics Pro
A professional Amazon review data analytics platform

## 📋 Project Overview

This is a Streamlit-based Amazon review analysis tool designed for in-depth analysis of Amazon product review data, providing smart translation, statistical analysis, keyword matching, and AI label classification.

**Development team**: Haiyi IDC Team  
**Maintenance**: @Ethan Zhou  
**Version**: v1.5.0  
**Last updated**: 2025-08-01  
**Data source**: Reviews exported in bulk via Shulex  
**Format**: .XLSX  

---

## 🎯 Project Background

### Why do we need this tool?

Shulex is currently one of the most mainstream CI tools. However, due to its limitations in how it filters the reviews to analyze, its internal matching logic, and its classification of review sentiment, its consumer insight conclusions can diverge to some extent from the real consumer population and their voices.

Take the insights for products related to the P7 project as an example: if insights into consumer demographics and needs are distorted, this can mislead the entire product process from development through launch and operations. Therefore, building on Shulex, we upgraded its analysis.

### AI Empowerment

AI delivers enormous empowerment and efficiency gains for the business. Taking CI analysis as an example, AI can extract key insights from consumer reviews and apply label classification to review content.

---

## 🚀 Core Features

### 📊 Data Preprocessing
- Automatically clean and standardize Amazon review data
- Support multiple data formats (Excel, CSV)
- Smart data validation and error handling
- Brand joining

### 🌐 Smart Translation
- Support Google Translate (free) and the Tencent Translation API (more accurate)
- **Smart cache system**: Automatically caches translation results to avoid repeated translation and greatly improve efficiency
- **Advanced filtering**: Precisely filter by brand, ASIN, rating, review type, and other dimensions
- **Row range control**: Set the start and end rows for translation to precisely control the translation scope
- Support batch translation of multiple text columns
- Automatically handle long texts by translating them in segments
- Smart error retry mechanism
- Real-time progress monitoring and cache hit statistics

### 📈 Statistical Analysis
- Comprehensive statistical analysis of review data, including sentiment analysis
- Multi-dimensional data visualization
- Rating distribution analysis
- Time trend analysis
- Brand comparison analysis

### 🎯 Keyword Matching
- Smart keyword matching and audience classification
- Preset categories: audience profiles, purchase motivations, user pain points
- Custom keyword configuration
- Precisely identify target users

### 🤖 AI Label Classification
- AI-powered review analysis & label classification
- Support multiple AI models
- Smart caching of AI analysis results
- Batch label classification

### ☁️ Word Cloud Analysis
- Smart word cloud generation
- Negative word filtering
- Word frequency analysis
- Custom stop words

### 💾 Smart Cache
- Automatically cache translation and AI results to avoid repeated processing
- Cache expiration management (auto-expires after 30 days)
- Cache statistics and cleanup tools
- Greatly improve processing efficiency

---

## 📁 Project Structure

```
new_Amazon_ReviewsAnalysis/
├── config/                    # 配置文件目录
│   ├── categories.json        # 预设类别配置
│   ├── negative_words.json    # 负面词汇配置
│   └── brand_data_example.csv # 品牌数据示例
├── pages/                     # 页面文件
│   ├── 0_Translation.py       # 评论翻译
│   ├── 1_Statistics.py        # 统计分析
│   ├── 2_WordCloud.py         # 词云分析
│   ├── 3_Keyword_Match.py     # 关键词匹配
│   └── 4_AI_Labeling.py       # AI标签分类
├── ai_label_cache/            # AI标签缓存
├── translation_cache/         # 翻译缓存
├── Home.py                    # 主页面
├── utils.py                   # 工具函数
├── clean_cache.py             # 缓存清理工具
└── README.md                  # 项目说明
```

---

## 🛠️ Installation & Running

### Environment Requirements
- Python 3.8+
- Streamlit 1.28.0+
- See `requirements.txt` for other dependencies

### Installation Steps

1. **Clone the project**:
```bash
git clone [项目地址]
cd new_Amazon_ReviewsAnalysis
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the app**:
```bash
streamlit run Home.py
```

---

## 📖 User Guide

### 1. Data Upload
- Supports Excel (.xlsx) and CSV formats
- Required columns: `Asin`, `Title`, `Content`, `Model`, `Rating`, `Date`
- Optional brand data file containing: `ASIN`, `Brand`, `Parent ASIN`

### 2. Data Preprocessing
- Automatically clean and standardize data
- Smart brand data association (dual-join logic)
- Data validation and error handling

### 3. Review Translation
- Select the columns to translate
- Configure the translation engine (Google/Tencent Translation API)
- Set filter conditions and translation scope
- Monitor translation progress in real time

### 4. Statistical Analysis
- View data overview and statistics
- Generate visualization charts
- Export analysis reports

### 5. Keyword Matching
- Use preset categories or custom keywords
- Perform audience classification and feature analysis
- Export matching results

### 6. AI Label Classification
- Configure AI models and API keys
- Run label classification in batch
- View classification results and statistics

---

## 🔧 Advanced Features

### Smart Cache System
- **Automatic caching**: Translation results are automatically saved to the local cache
- **Cache expiration**: Auto-expires after 30 days, preventing the cache from taking up too much space
- **Cache statistics**: Real-time display of cache file count and size
- **Cache cleanup**: Clean up expired cache files with one click
- **Cache hits**: Translations use the cache first, greatly improving speed

### Dual Brand Data Join
- **First-round matching**: Join the review data's Asin with the brand data's ASIN
- **Second-round matching**: Join unmatched records using the review data's Asin against the brand data's Parent ASIN
- **Smart detection**: Automatically detect whether the brand data contains a Parent ASIN column
- **Detailed statistics**: Show match rates, per-round matching results, and more

### Advanced Filtering
- **Brand filter**: Translate product reviews for selected brands
- **ASIN filter**: Translate reviews for selected products
- **Rating filter**: Filter reviews by rating level (1-5 stars)
- **Review type filter**: Filter by review type (positive/neutral/negative)
- **Row range filter**: Set the start and end rows for translation
- **Combined filtering**: Support combining multiple filter conditions

---

## ⚙️ Configuration

### Tencent Translation API Configuration
To use the Tencent Translation API for more accurate translation results:

1. **Get API keys**:
   - Log in to the [Tencent Cloud Console](https://console.cloud.tencent.com/)
   - Go to "Access Management" → "API Key Management"
   - Create a new API key
   - Copy the SecretId and SecretKey

2. **Enable the service**:
   - Make sure the Machine Translation service is enabled
   - Select "Tencent Translation API" on the translation page
   - Enter the SecretId and SecretKey

### AI Model Configuration
Multiple AI models are supported:
- **OpenAI**: Requires an OpenAI API key
- **Deepseek**: Requires a Deepseek API key
- **Alibaba Qwen**: Requires an Alibaba Cloud API key

### Cache Management
```bash
# 清理过期缓存
python clean_cache.py
```

---

## 📊 Preset Categories

### Audience Profiles
- Pregnant or breastfeeding women
- Seniors
- Children
- Fitness enthusiasts
- Vegetarians

### Purchase Motivations
- Health improvement
- Beauty and skincare
- Weight management
- Sleep improvement
- Digestive health

### User Pain Points
- Side effects
- Ineffective results
- Price issues
- Taste issues
- Packaging issues

---

## 🔄 Version History

- **v1.5.0** (2025-08-01): 
  - Dual brand data join optimization
  - Configuration file restructuring
  - Performance optimization and code cleanup
  - Cache management fixes

- **v1.4.0**: 
  - AI label classification feature
  - Word cloud analysis feature
  - Smart cache system

- **v1.3.0**: 
  - Added smart caching and advanced filtering
  - Greatly improved translation efficiency

- **v1.2.0**: 
  - Added review translation
  - Support for Google Translate and the Tencent Translation API

- **v1.1.2**: 
  - Optimized data processing and visualization

- **v1.1.0**: 
  - Initial feature implementation

---

## 🛠️ Maintenance Tools

### Cache Cleanup
```bash
python clean_cache.py
```

### Project Optimization
- Run cache cleanup regularly
- Monitor cache size and performance
- Avoid adding duplicate code
- New configuration files should be placed in the `config/` directory

---

## 📞 Technical Support

- **Development team**: Haiyi IDC Team
- **Maintenance**: @Ethan Zhou
- **Email**: idc@oceanwing.com
- **Version**: v1.5.0
- **Last updated**: 2025-08-01

---

## 📄 License

This project is for internal use within Haiyi only, and the copyright belongs to the Haiyi IDC Team.

---

**Wishing you smooth sailing and good health** 
