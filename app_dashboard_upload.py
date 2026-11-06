import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dynamic Excel Dashboard", layout="wide")

# --- KHU VỰC CẤU HÌNH GIAO DIỆN Ở SIDEBAR ---

text_color = "#007BFF"
font_size = 35

# st.sidebar.markdown("---")
st.markdown(
    f"<h1 style='text-align: center; color: {text_color}; font-size: {font_size}px; font-family: sans-serif;'>"
    f"🖥️ TRÌNH DỰNG DASHBOARD ĐA NĂNG"
    f"</h1>", 
    unsafe_allow_html=True
)

st.markdown("---")

st.sidebar.header("📂 Nguồn dữ liệu đầu vào")

# 1. Widget cho phép người dùng tải file Excel hoặc CSV từ máy tính của họ lên web
uploaded_file = st.sidebar.file_uploader("Tải lên file báo cáo (Excel hoặc CSV):", type=["xlsx", "xls", "csv"])

# --- HÀM ĐỌC DỮ LIỆU ĐỘNG ---
@st.cache_data # Mẹo tối ưu: Giúp ghi nhớ dữ liệu đã đọc, không bị load lại file khi chỉnh màu chữ
def load_data(file):
    _, ext = os.path.splitext(file.name)
    if ext.lower() == '.csv':
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# Xử lý logic nếu có file được tải lên
if uploaded_file is not None:
    # Đọc dữ liệu từ file người dùng upload
    df_raw = load_data(uploaded_file)

    # Hiển thị tiêu đề động tùy biến màu sắc
    st.markdown(
        f"<h1 style='text-align: center; color: {text_color}; font-size: {font_size}px; font-family: sans-serif;'>"
        f"📊 PHÂN TÍCH DỮ LIỆU file: {uploaded_file.name}"
        f"</h1>", 
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # 2. BỘ LỌC ĐỘNG TỰ ĐỘNG THEO CỘT CỦA FILE
    # Tự động lấy danh sách tên các cột trong file để người dùng chọn cột phân tích
    all_columns = df_raw.columns.tolist()
    
    st.sidebar.subheader("⚙️ Cấu hình bộ lọc & Trục biểu đồ")
    column_to_filter = st.sidebar.selectbox("Chọn **:red[cột]** dùng làm **:blue[Bộ lọc]**:", options=all_columns, index=0)
    
    # Lấy các giá trị duy nhất của cột được chọn làm bộ lọc
    unique_values = df_raw[column_to_filter].unique().tolist()
    selected_values = st.sidebar.multiselect(
        f"Lọc giá trị theo nhóm '{column_to_filter}':", 
        options=unique_values, 
        default=unique_values
    )
    
    # Chọn trục tọa độ cho biểu đồ dựa trên các cột sẵn có của file
    x_axis = st.sidebar.selectbox("Chọn cột làm **:red[trục X]** (Mục **:blue[phân tích]**):", options=all_columns, index=min(1, len(all_columns)-1))
    y_axis = st.sidebar.selectbox("Chọn cột làm **:blue[trục Y]** (**:red[Số liệu/Doanh thu]**):", options=all_columns, index=min(2, len(all_columns)-1))
    
    # Tiến hành lọc dữ liệu theo tùy chọn của người dùng
    filtered_df = df_raw[df_raw[column_to_filter].isin(selected_values)]
    
    # --- HIỂN THỊ KẾT QUẢ TRÊN GIAO DIỆN CHÍNH ---
    col_table, col_chart = st.columns([2, 3]) # Cột biểu đồ chiếm 60% chiều rộng, cột bảng chiếm 40%
    
    with col_table:
        st.markdown(f"<h3 style='color: {text_color};'>📋 Bảng dữ liệu đã lọc</h3>", unsafe_allow_html=True)
        st.dataframe(filtered_df, width="stretch", hide_index=True)
        
    with col_chart:
        st.markdown(f"<h3 style='color: {text_color};'>📈 Biểu đồ trực quan hóa dữ liệu</h3>", unsafe_allow_html=True)
        
        if not filtered_df.empty:
            # Tạo biểu đồ cột động linh hoạt theo lựa chọn cột của người dùng
            fig = px.bar(
                filtered_df, 
                x=x_axis, 
                y=y_axis, 
                color=column_to_filter, 
                barmode='group',
                text=y_axis
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, width="stretch")
        else:
            st.warning("⚠️ Không có dữ liệu nào khớp với bộ lọc hiện tại.")

else:
    st.success("💡 Vui lòng tải một **:orange[file dữ liệu báo cáo]** dạng **:red[Excel (.xlsx)]** hoặc **:red[CSV]** ở **:violet[thanh bên (*Sidebar*)]** để bắt đầu xây dựng Dashboard tự động.")
    st.error('File dữ liệu báo cáo nên có tối thiểu **:green[3 cột]** để làm **:blue[bộ lọc]**, làm **:blue[trục X]** và **:blue[trục Y]**')
    st.success("💡 Dưới đây là dữ liệu làm mẫu có **:violet[4 cột]** với **:red[cột Tháng]** làm **:gray[bộ lọc]**, **:red[cột Sản phẩm]** làm **:gray[trục X]** và **:red[cột Doanh thu  ($)]** làm **:gray[trục Y]**.")
    
    # Giao diện chào mừng khi chưa có file nào được tải lên
    data_mau = pd.DataFrame({
        'Tháng': ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4'],
        'Sản phẩm': ['Điện thoại', 'Điện thoại', 'Điện thoại', 'Điện thoại', 'Laptop', 'Laptop', 'Laptop', 'Laptop'],
        'Số lượng bán': [60, 75, 90, 120, 90, 110, 130, 170],
        'Doanh thu ($)': [60000, 75000, 90000, 120000, 90000, 110000, 130000, 170000]
    })

    # Bảng dữ liệu mẫu
    # --- HIỂN THỊ KẾT QUẢ TRÊN GIAO DIỆN CHÍNH ---
    col_table, col_chart = st.columns([2, 3]) # Cột biểu đồ chiếm 60% chiều rộng, cột bảng chiếm 40%
    
    with col_table:
        st.markdown(f"<h3 style='color: {text_color};'>📋 Bảng dữ liệu mẫu đã lọc</h3>", unsafe_allow_html=True)
        st.dataframe(data_mau, width="stretch", hide_index=True)
        
    with col_chart:
        st.markdown(f"<h3 style='color: {text_color};'>📈 Biểu đồ trực quan hóa dữ liệu mẫu</h3>", unsafe_allow_html=True)
        # Tạo biểu đồ cột động linh hoạt theo lựa chọn cột của người dùng
        fig_mau = px.bar(
            data_mau, 
            x='Sản phẩm', 
            y='Doanh thu ($)', 
            color='Tháng', 
            barmode='group',
            text='Doanh thu ($)'
        )
        fig_mau.update_traces(textposition="outside")
        st.plotly_chart(fig_mau, width="stretch")
        
        
    st.markdown("---")
    
    # Bạn có thể dùng file dữ liệu cũ tự gõ ở lượt trước lưu thành file .csv để test thử tính năng này!
