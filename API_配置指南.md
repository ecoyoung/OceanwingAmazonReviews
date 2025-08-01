# AI API 配置指南
# 我个人推荐使用便宜的deepseek
## 🔧 支持的AI模型

### 1. OpenAI GPT
- **API Key获取**: 访问 https://platform.openai.com/api-keys
- **格式**: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **费用**: 按使用量计费，约$0.002/1K tokens

### 2. Deepseek
- **API Key获取**: 访问 https://platform.deepseek.com/api_keys
- **格式**: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **费用**: 按使用量计费，价格相对较低

### 3. 阿里千问
- **API Key获取**: 访问 https://dashscope.console.aliyun.com/apiKey
- **格式**: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **费用**: 按使用量计费

## 🚀 使用步骤

1. **获取API Key**: 访问对应平台的官网注册账号并获取API Key
2. **测试连接**: 在应用中点击"🧪 测试API连接"按钮验证配置
3. **开始标注**: 配置成功后即可开始批量AI标注

## ⚠️ 常见问题

### 404错误
- **原因**: API端点配置错误或API Key无效
- **解决**: 检查API Key是否正确，确认模型选择正确

### 401错误
- **原因**: API Key无效或已过期
- **解决**: 重新生成API Key

### 429错误
- **原因**: API调用频率过高
- **解决**: 降低并发线程数，等待一段时间后重试

### 网络超时
- **原因**: 网络连接不稳定
- **解决**: 检查网络连接，稍后重试

## 💡 使用建议

1. **首次使用**: 建议先用少量数据测试
2. **并发设置**: 建议设置为2-5个线程，避免API限流
3. **缓存机制**: 系统会自动缓存结果，避免重复调用
4. **成本控制**: 监控API使用量，控制成本

## 🔍 故障排除

如果遇到问题，请按以下步骤排查：

1. 检查API Key是否正确
2. 确认网络连接正常
3. 尝试降低并发线程数
4. 查看错误信息中的具体提示
5. 联系技术支持

## 📞 技术支持

如有问题，请提供以下信息：
- 使用的AI模型
- 错误信息截图
- API Key格式（隐藏敏感信息）
- 网络环境描述 