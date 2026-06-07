import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Tải dữ liệu từ tệp CSV
df = pd.read_csv('260603_1540_Qwen-Qwen2.5-Coder-7B-Instruct_all_per_sample_metrics.csv')

# Loại bỏ các giá trị khuyết thiếu (NaN) để vẽ biểu đồ chính xác
plot_data = df[['kendall', 'spearman']].dropna()

# Tạo khung chứa 2 biểu đồ con song song
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

# Vẽ biểu đồ Histogram cho chỉ số Kendall Tau
sns.histplot(plot_data['kendall'], kde=True, ax=axes[0], color='skyblue', bins=20)
axes[0].set_title('Distribution of Kendall Tau')
axes[0].set_xlabel('Kendall Tau')
axes[0].set_ylabel('Count')

# Vẽ biểu đồ Histogram cho chỉ số Spearman
sns.histplot(plot_data['spearman'], kde=True, ax=axes[1], color='salmon', bins=20)
axes[1].set_title('Distribution of Spearman Correlation')
axes[1].set_xlabel('Spearman')

# Tối ưu không gian hiển thị và lưu hình ảnh
plt.tight_layout()
plt.savefig('kendall_spearman_histplot.png')