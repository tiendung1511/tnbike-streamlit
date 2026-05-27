import streamlit as st
from forecast_model import run_forecast

st.set_page_config(
    page_title="TNBIKE FORECAST",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================
with st.spinner("Đang chạy mô hình Machine Learning..."):
    forecast_df = run_forecast()

st.success("Dự báo hoàn tất!")

# =========================
# SIDEBAR (GIỐNG DASHBOARD)
# =========================
with st.sidebar:
    st.title("⚙️ Cấu hình dự báo")

    st.subheader("Chọn ngày dự báo")

    selected_index = st.slider(
        "Số ngày dự báo",
        min_value=0,
        max_value=len(forecast_df) - 1,
        value=0
    )

    selected_row = forecast_df.iloc[selected_index]
    selected_date = selected_row["Date"]
    selected_revenue = selected_row["Forecast Revenue"]

    selected_week = selected_date.isocalendar().week

    week_data = forecast_df[
        forecast_df["Date"].dt.isocalendar().week == selected_week
    ]

    weekly_revenue = week_data["Forecast Revenue"].sum()

# =========================
# HEADER
# =========================
st.title("📊 TNBIKE FORECAST SYSTEM")
st.write("Hệ thống AI dự báo doanh thu Quý 2/2026")

# =========================
# KPI ROW (GIỐNG DASHBOARD CARD)
# =========================
total_forecast = forecast_df["Forecast Revenue"].sum()

max_day = forecast_df.loc[forecast_df["Forecast Revenue"].idxmax()]

business_days = forecast_df[forecast_df["Forecast Revenue"] > 0]
min_day = business_days.loc[business_days["Forecast Revenue"].idxmin()]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Tổng doanh thu dự báo", f"{total_forecast:,.0f} VND")

with col2:
    st.metric("Ngày doanh thu cao nhất", f"{max_day['Forecast Revenue']:,.0f} VND")

with col3:
    st.metric("Ngày doanh thu thấp nhất", f"{min_day['Forecast Revenue']:,.0f} VND")

# =========================
# MAIN 2-COLUMN LAYOUT (GIỐNG SLIDE)
# =========================
left, right = st.columns([1.2, 1])

# -------------------------
# LEFT: DAILY + WEEKLY VIEW
# -------------------------
with left:
    st.subheader(" Tra cứu doanh thu")

    st.markdown(
        f"""
        **Ngày:** `{selected_date.date()}`  
        **Tuần:** `{selected_week}`
        """
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Doanh thu ngày chọn",
        f"{selected_revenue:,.0f} VND"
    )

    c2.metric(
        f"Tổng doanh thu tuần {selected_week}",
        f"{weekly_revenue:,.0f} VND"
    )

    st.subheader(" Biểu đồ dự báo")
    st.line_chart(forecast_df.set_index("Date")["Forecast Revenue"])

# -------------------------
# RIGHT: INSIGHT PANEL
# -------------------------
with right:
    st.subheader(" Thông tin chi tiết")

    st.markdown("###  Ngày cao nhất")
    st.write(
        f"{max_day['Date'].date()} — {max_day['Forecast Revenue']:,.0f} VND"
    )

    st.markdown("###  Ngày thấp nhất")
    st.write(
        f"{min_day['Date'].date()} — {min_day['Forecast Revenue']:,.0f} VND"
    )

    st.subheader(" Cảnh báo rủi ro")
    st.info(
        "- Dự báo mang tính xác suất\n"
        "- Có thể biến động theo thị trường\n"
        "- Nên kết hợp chiến lược quản trị rủi ro"
    )

# =========================
# DATA TABLE (COLLAPSIBLE)
# =========================
with st.expander(" Xem bảng dữ liệu dự báo"):
    st.dataframe(forecast_df, use_container_width=True)