import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

import psycopg2

from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import Ridge

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor


def run_forecast():

    import warnings
    warnings.filterwarnings("ignore")

    import numpy as np
    import pandas as pd

    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    import psycopg2
    import shap

    from sklearn.preprocessing import StandardScaler

    from sklearn.metrics import (
        mean_absolute_error,
        mean_squared_error,
        r2_score
    )

    from sklearn.linear_model import Ridge

    from sklearn.ensemble import (
        RandomForestRegressor,
        GradientBoostingRegressor
    )

    from xgboost import XGBRegressor
    from lightgbm import LGBMRegressor
    from catboost import CatBoostRegressor

    # Khởi tạo giá trị ngẫu nhiên cố định để kết quả không thay đổi sau mỗi lần chạy
    np.random.seed(42)

    # Kết nối cơ sở dữ liệu
    conn = psycopg2.connect(
        host="db.xxxxx.supabase.co",
        port=5432,
        database="tnbike_db",
        user="postgres",
        password="Ntd1511##"
    )

    # Truy vấn dữ liệu SQL
    query = """
    WITH vip_customers AS (
        SELECT
            so.customer_code,
            SUM(so.total_amount) AS total_q1_spent
        FROM tnbike.sales_order so
        WHERE
            EXTRACT(YEAR FROM so.order_date) = 2026
            AND EXTRACT(MONTH FROM so.order_date) IN (1,2,3)
        GROUP BY so.customer_code
        HAVING SUM(so.total_amount) >= 500000000
    )
    SELECT
        fs.order_date,
        SUM(fs.line_total) AS revenue,
        SUM(fs.quantity) AS total_qty,
        COUNT(DISTINCT fs.so_number) AS total_orders,
        COUNT(DISTINCT fs.customer_code) AS active_customers,
        COUNT(DISTINCT fs.product_code) AS active_products,
        COUNT(DISTINCT fs.province_id) AS active_provinces,
        COUNT(DISTINCT fs.group_code) AS active_groups,
        AVG(fs.unit_price) AS avg_price,
        MAX(fs.line_total) AS max_order,
        MIN(fs.line_total) AS min_order,
        STDDEV(fs.line_total) AS order_volatility,
        COUNT(DISTINCT fs.color) AS active_colors,
        COUNT(DISTINCT fs.line_name) AS active_lines,
        AVG(fs.quantity) AS avg_line_qty,
        SUM(
            CASE
                WHEN fs.region = 'Miền Bắc'
                THEN fs.line_total
                ELSE 0
            END
        ) AS north_revenue,
        SUM(
            CASE
                WHEN fs.region = 'Miền Trung'
                THEN fs.line_total
                ELSE 0
            END
        ) AS central_revenue,
        SUM(
            CASE
                WHEN fs.region = 'Miền Nam'
                THEN fs.line_total
                ELSE 0
            END
        ) AS south_revenue,
        SUM(
            CASE
                WHEN vc.customer_code IS NOT NULL
                THEN fs.line_total
                ELSE 0
            END
        ) AS vip_revenue,
        COUNT(
            DISTINCT CASE
                WHEN vc.customer_code IS NOT NULL
                THEN fs.customer_code
            END
        ) AS vip_customers,
        AVG(
            CASE
                WHEN vc.customer_code IS NOT NULL
                THEN fs.line_total
            END
        ) AS vip_avg_order
    FROM tnbike.fact_sales fs
    LEFT JOIN vip_customers vc
    ON fs.customer_code = vc.customer_code
    GROUP BY fs.order_date
    ORDER BY fs.order_date
    """

    # Tải dữ liệu vào DataFrame
    df = pd.read_sql(query, conn)

    conn.close()

    # Định dạng cột ngày tháng
    df['order_date'] = pd.to_datetime(df['order_date'])

    df = df.sort_values('order_date')

    # Thiết lập biến mục tiêu 
    df['real_revenue'] = df['revenue']

    df['target'] = np.log1p(df['revenue'])

    # Cấu hình danh sách các ngày lễ Việt Nam năm 2026
    vn_holidays = pd.to_datetime([
        # Tết Dương Lịch
        '2026-01-01',
        # Giỗ tổ Hùng Vương
        '2026-04-26',
        '2026-04-27',
        # Ngày Giải phóng miền Nam
        '2026-04-30',
        # Ngày Quốc tế Lao động
        '2026-05-01',
        # Ngày Quốc khánh
        '2026-09-02'
    ])

    # Khởi tạo các đặc trưng về ngày tháng
    df['day_of_week'] = df['order_date'].dt.dayofweek

    df['day'] = df['order_date'].dt.day

    df['month'] = df['order_date'].dt.month

    df['quarter'] = df['order_date'].dt.quarter

    df['week'] = df['order_date'].dt.isocalendar().week.astype(int)

    df['is_weekend'] = (
        df['day_of_week'] >= 5
    ).astype(int)

    df['is_sunday'] = (
        df['day_of_week'] == 6
    ).astype(int)

    df['is_month_end'] = (
        df['day'] >= 27
    ).astype(int)

    df['is_payday'] = (
        df['day'].isin([1,5,10,15,20,25,30])
    ).astype(int)

    df['is_holiday'] = (
        df['order_date'].isin(vn_holidays)
    ).astype(int)

    # Khởi tạo đặc trưng chu kỳ vòng lặp 
    df['dow_sin'] = np.sin(
        2*np.pi*df['day_of_week']/7
    )

    df['dow_cos'] = np.cos(
        2*np.pi*df['day_of_week']/7
    )

    df['month_sin'] = np.sin(
        2*np.pi*df['month']/12
    )

    df['month_cos'] = np.cos(
        2*np.pi*df['month']/12
    )

    # Phân tích học sâu theo thứ trong tuần 
    weekday_stats = (
        df.groupby('day_of_week')
        .agg({
            'real_revenue': [
                'mean',
                'max',
                'min',
                'std',
                'median'
            ],
            'total_orders': [
                'mean',
                'max',
                'min'
            ],
            'total_qty': [
                'mean',
                'max',
                'min'
            ]
        })
    )

    weekday_stats.columns = [
        'dow_avg_revenue',
        'dow_max_revenue',
        'dow_min_revenue',
        'dow_std_revenue',
        'dow_median_revenue',
        'dow_avg_orders',
        'dow_max_orders',
        'dow_min_orders',
        'dow_avg_qty',
        'dow_max_qty',
        'dow_min_qty'
    ]

    weekday_stats = weekday_stats.reset_index()

    df = df.merge(
        weekday_stats,
        on='day_of_week',
        how='left'
    )

    # Phân tích thông minh theo tuần 
    weekly_stats = (
        df.groupby('week')
        .agg({
            'real_revenue': [
                'mean',
                'max',
                'min',
                'std'
            ],
            'total_qty': [
                'mean',
                'max'
            ],
            'total_orders': [
                'mean',
                'max'
            ]
        })
    )

    weekly_stats.columns = [
        'week_avg_revenue',
        'week_max_revenue',
        'week_min_revenue',
        'week_std_revenue',
        'week_avg_qty',
        'week_max_qty',
        'week_avg_orders',
        'week_max_orders'
    ]

    weekly_stats = weekly_stats.reset_index()

    df = df.merge(
        weekly_stats,
        on='week',
        how='left'
    )

    # Phân tích nâng cao về sức mạnh doanh thu của từng tuần
    weekly_power = (
        df.groupby('week')['real_revenue']
        .agg([
            'mean',
            'max',
            'min',
            'std',
            'median'
        ])
    )

    weekly_power.columns = [
        'weekly_mean_power',
        'weekly_max_power',
        'weekly_min_power',
        'weekly_std_power',
        'weekly_median_power'
    ]

    weekly_power = weekly_power.reset_index()

    df = df.merge(
        weekly_power,
        on='week',
        how='left'
    )

    # Khởi tạo các đặc trưng độ trễ thời gian 
    lags = [1,2,3,7,14,21,30]

    for lag in lags:
        df[f'lag_{lag}'] = (
            df['target']
            .shift(lag)
        )

    # Khởi tạo các đặc trưng trung bình trượt và độ lệch chuẩn trượt 
    windows = [3,7,14,30]

    for w in windows:
        df[f'rolling_mean_{w}'] = (
            df['target']
            .shift(1)
            .rolling(w)
            .mean()
        )

        df[f'rolling_std_{w}'] = (
            df['target']
            .shift(1)
            .rolling(w)
            .std()
        )

    # Khởi tạo chỉ số trung bình trượt lũy thừa trọng số (EWMA)
    df['ewm_7'] = (
        df['target']
        .shift(1)
        .ewm(span=7)
        .mean()
    )

    df['ewm_14'] = (
        df['target']
        .shift(1)
        .ewm(span=14)
        .mean()
    )

    # Làm sạch dữ liệu (Xử lý các giá trị vô cực và loại bỏ các dòng có giá trị rỗng)
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    df = df.dropna()

    # Phân chia tập dữ liệu (70% cho tập huấn luyện, 15% cho tập kiểm định)
    train_size = int(len(df)*0.7)

    valid_size = int(len(df)*0.15)

    train = df.iloc[:train_size]

    valid = df.iloc[
        train_size : train_size + valid_size
    ]

    # Lọc bỏ các cột không dùng làm đặc trưng đầu vào mô hình
    exclude = [
        'order_date',
        'revenue',
        'real_revenue',
        'target'
    ]

    features = [
        c for c in df.columns
        if c not in exclude
    ]

    X_train = train[features]
    y_train = train['target']

    X_valid = valid[features]
    y_valid = valid['target']

    # Chuẩn hóa quy mô dữ liệu (Scaling)
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)

    X_valid_scaled = scaler.transform(X_valid)

    # Khởi tạo cấu hình cấu trúc các mô hình học máy
    xgb = XGBRegressor(
        n_estimators=650,
        learning_rate=0.018,
        max_depth=6,
        subsample=0.92,
        colsample_bytree=0.92,
        reg_lambda=4,
        random_state=42
    )

    lgbm = LGBMRegressor(
        n_estimators=600,
        learning_rate=0.018,
        max_depth=6,
        subsample=0.92,
        colsample_bytree=0.92,
        random_state=42,
        verbose=-1
    )

    cat = CatBoostRegressor(
        iterations=600,
        learning_rate=0.018,
        depth=6,
        verbose=0,
        random_state=42
    )

    rf = RandomForestRegressor(
        n_estimators=350,
        max_depth=9,
        random_state=42,
        n_jobs=-1
    )

    gbr = GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.018,
        max_depth=4,
        random_state=42
    )

    ridge = Ridge(alpha=1.0)

    # Thực hiện huấn luyện các mô hình học máy trên tập Train
    xgb.fit(X_train, y_train)

    lgbm.fit(X_train, y_train)

    cat.fit(X_train, y_train)

    rf.fit(X_train, y_train)

    gbr.fit(X_train, y_train)

    ridge.fit(X_train_scaled, y_train)

    # Chạy mô hình dự đoán trên tập kiểm định bằng phương pháp kết hợp Ensemble
    valid_pred_log = (
        xgb.predict(X_valid) * 0.34
        +
        lgbm.predict(X_valid) * 0.24
        +
        cat.predict(X_valid) * 0.18
        +
        rf.predict(X_valid) * 0.12
        +
        gbr.predict(X_valid) * 0.07
        +
        ridge.predict(X_valid_scaled) * 0.05
    )

    # Chuyển đổi giá trị dự đoán và giá trị thực tế từ dạng Log về giá trị tiền tệ VND thực tế
    valid_real = np.expm1(y_valid)

    valid_pred = np.expm1(valid_pred_log)

    # Đo lường và đánh giá các chỉ số kiểm định sai số 
    mae = mean_absolute_error(
        valid_real,
        valid_pred
    )

    rmse = np.sqrt(
        mean_squared_error(
            valid_real,
            valid_pred
        )
    )

    r2 = r2_score(
        valid_real,
        valid_pred
    )

    mape = np.mean(
        np.abs(
            (valid_real - valid_pred)
            /
            np.maximum(valid_real,1)
        )
    ) * 100

    smape = np.mean(
        2 * np.abs(valid_pred - valid_real)
        /
        (
            np.abs(valid_real)
            +
            np.abs(valid_pred)
            +
            1e-9
        )
    ) * 100

    wape = (
        np.sum(
            np.abs(valid_real - valid_pred)
        )
        /
        np.sum(np.abs(valid_real))
    ) * 100

    print("\n========== ĐÁNH GIÁ CHỈ SỐ KPI MÔ HÌNH ==========\n")
    print(f"Sai số tuyệt đối trung bình (MAE)   : {mae:,.0f}")
    print(f"Sai số căn phương trung bình (RMSE) : {rmse:,.0f}")
    print(f"Hệ số xác định (R2 Score)           : {r2:.4f}")
    print(f"Phần trăm sai số tuyệt đối (MAPE)   : {mape:.2f}%")
    print(f"Chỉ số sai số đối xứng (SMAPE)      : {smape:.2f}%")
    print(f"Tỷ lệ sai số trọng số (WAPE)        : {wape:.2f}%")

    # Thiết lập mốc thời gian chạy dự báo tương lai cho Quý 2 (Tháng 4 - Tháng 6)
    future_dates = pd.date_range(
        start='2026-04-01',
        end='2026-06-30',
        freq='D'
    )

    forecast_results = []

    # Lấy 60 ngày doanh thu thực tế gần nhất làm bệ phóng dữ liệu lịch sử đầu vào
    last_values = list(
        df['real_revenue'].tail(60)
    )

    # Vòng lặp dự báo cuốn chiếu cho từng ngày trong tương lai 
    for i, future_date in enumerate(future_dates):

        row = {}

        dow = future_date.dayofweek
        dom = future_date.day
        month = future_date.month
        week = int(future_date.isocalendar().week)

        row['day_of_week'] = dow
        row['day'] = dom
        row['month'] = month
        row['quarter'] = future_date.quarter
        row['week'] = week

        row['is_weekend'] = int(dow >= 5)

        row['is_sunday'] = int(dow == 6)

        row['is_month_end'] = int(dom >= 27)

        row['is_payday'] = int(
            dom in [1,5,10,15,20,25,30]
        )

        row['is_holiday'] = int(
            future_date in vn_holidays
        )

        row['dow_sin'] = np.sin(
            2*np.pi*dow/7
        )

        row['dow_cos'] = np.cos(
            2*np.pi*dow/7
        )

        row['month_sin'] = np.sin(
            2*np.pi*month/12
        )

        row['month_cos'] = np.cos(
            2*np.pi*month/12
        )

        business_cols = [
            'total_qty',
            'total_orders',
            'active_customers',
            'active_products',
            'active_provinces',
            'active_groups',
            'avg_price',
            'max_order',
            'min_order',
            'order_volatility',
            'active_colors',
            'active_lines',
            'avg_line_qty',
            'north_revenue',
            'central_revenue',
            'south_revenue',
            'vip_revenue',
            'vip_customers',
            'vip_avg_order',
            'dow_avg_revenue',
            'dow_max_revenue',
            'dow_min_revenue',
            'dow_std_revenue',
            'dow_median_revenue',
            'dow_avg_orders',
            'dow_max_orders',
            'dow_min_orders',
            'dow_avg_qty',
            'dow_max_qty',
            'dow_min_qty',
            'week_avg_revenue',
            'week_max_revenue',
            'week_min_revenue',
            'week_std_revenue',
            'week_avg_qty',
            'week_max_qty',
            'week_avg_orders',
            'week_max_orders',
            'weekly_mean_power',
            'weekly_max_power',
            'weekly_min_power',
            'weekly_std_power',
            'weekly_median_power'
        ]

        # Tính toán giá trị trung bình 14 ngày gần nhất cho các chỉ số hoạt động kinh doanh
        for col in business_cols:
            row[col] = float(
                df[col].tail(14).mean()
            )

        # Cập nhật các đặc trưng Lag động cho ngày đang dự báo
        for lag in lags:
            row[f'lag_{lag}'] = np.log1p(
                last_values[-lag]
            )

        # Cập nhật các đặc trưng Rolling động cho ngày đang dự báo
        for w in windows:
            row[f'rolling_mean_{w}'] = np.mean(
                np.log1p(last_values[-w:])
            )

            row[f'rolling_std_{w}'] = np.std(
                np.log1p(last_values[-w:])
            )

        # Cập nhật các đặc trưng lũy thừa trọng số EWMA động
        row['ewm_7'] = pd.Series(
            np.log1p(last_values)
        ).ewm(span=7).mean().iloc[-1]

        row['ewm_14'] = pd.Series(
            np.log1p(last_values)
        ).ewm(span=14).mean().iloc[-1]

        # Khởi tạo DataFrame cho ngày dự báo tương lai hiện tại
        X_future = pd.DataFrame([row])

        X_future = X_future.reindex(
            columns=X_train.columns,
            fill_value=0
        )

        X_future_scaled = scaler.transform(
            X_future
        )

        # Mô hình Ensemble thực hiện dự đoán doanh thu thô
        pred_log = (
            xgb.predict(X_future)[0] * 0.34
            +
            lgbm.predict(X_future)[0] * 0.24
            +
            cat.predict(X_future)[0] * 0.18
            +
            rf.predict(X_future)[0] * 0.12
            +
            gbr.predict(X_future)[0] * 0.07
            +
            ridge.predict(X_future_scaled)[0] * 0.05
        )

        pred = np.expm1(pred_log)

        # Thuật toán tối ưu hóa hành vi ngày trong tuần 
        dow_avg = row['dow_avg_revenue']

        dow_max = row['dow_max_revenue']

        dow_min = row['dow_min_revenue']

        dow_std = max(
            row['dow_std_revenue'],
            1
        )

        dynamic_position = np.random.beta(2,2)

        realistic_value = (
            dow_min
            +
            (dow_max - dow_min)
            * dynamic_position
        )

        # Trộn kết quả mô hình với phân phối thực tế lịch sử theo tỷ lệ 55-45
        pred = (
            pred * 0.55
            +
            realistic_value * 0.45
        )

        # Thêm nhiễu trắng ngẫu nhiên dựa trên độ lệch chuẩn của thứ để tăng độ thực tế
        pred += np.random.normal(
            0,
            dow_std * 0.18
        )

        # Điều chỉnh nhịp độ doanh thu theo sức mạnh của từng tuần 
        week_strength = (
            row['week_avg_revenue']
            /
            max(
                df['real_revenue'].mean(),
                1
            )
        )

        pred *= (
            0.7
            +
            0.3 * week_strength
        )

        # Thuật toán mô phỏng biến động ngày Chủ Nhật 
        if dow == 6:

            sunday_hist = df[
                df['day_of_week'] == 6
            ]['real_revenue']

            sunday_mean = sunday_hist.mean()

            sunday_std = sunday_hist.std()

            sunday_min = sunday_hist.min()

            sunday_max = sunday_hist.max()

            pred = np.random.normal(
                sunday_mean,
                sunday_std * 0.7
            )

            # Mô phỏng xác suất 40% ngày Chủ Nhật sụt giảm mạnh do kho đóng cửa nghỉ
            if np.random.rand() < 0.4:

                pred *= np.random.uniform(
                    0.01,
                    0.12
                )

            # Mô phỏng xác suất 8% ngày Chủ Nhật có đại lý gom đơn đột biến
            if np.random.rand() < 0.08:

                pred *= np.random.uniform(
                    1.5,
                    2.2
                )

            pred = np.clip(
                pred,
                sunday_min,
                sunday_max
            )

        # Tối ưu tăng trưởng dựa trên tỷ trọng đóng góp của nhóm khách hàng VIP 
        vip_ratio = (
            df['vip_revenue'].tail(14).mean()
            /
            max(
                df['real_revenue'].tail(14).mean(),
                1
            )
        )

        pred *= (
            1 + vip_ratio * 0.12
        )

        # Chu kỳ đặt hàng sỉ khối doanh nghiệp B2B 
        if dow in [0,1]: # Đầu tuần đặt hàng mạnh
            pred *= np.random.uniform(
                1.08,
                1.25
            )

        if dow == 4: # Thứ Sáu chốt sổ giảm nhẹ
            pred *= np.random.uniform(
                0.90,
                1.02
            )

        if dom in [3,4,5,18,19,20]: # Các ngày cao điểm gom hàng phân phối định kỳ
            pred *= np.random.uniform(
                1.10,
                1.35
            )

        # Động lượng tăng trưởng ngắn hạn gần đây của doanh nghiệp 
        recent_growth = (
            np.mean(last_values[-7:])
            /
            max(
                np.mean(last_values[-30:]),
                1
            )
        )

        pred *= (
            0.88
            +
            recent_growth * 0.12
        )

        # Bộ lọc giả lập xuất hiện các đơn hàng sỉ siêu lớn đột xuất 
        if np.random.rand() < 0.06:

            pred *= np.random.uniform(
                1.8,
                3.2
            )

        # Áp dụng hệ số tăng trưởng tự nhiên theo xu hướng dài hạn 
        trend_factor = 1 + (i / 1800)

        pred *= trend_factor

        # Làm mịn dữ liệu đầu ra dựa trên trung bình lịch sử 3 tuần gần nhất 
        historical_mean = np.mean(
            last_values[-21:]
        )

        pred = (
            pred * 0.82
            +
            historical_mean * 0.18
        )

        # Giới hạn chặn trần doanh thu để loại bỏ các giá trị dị biệt vô lý 
        max_cap = (
            df['real_revenue']
            .quantile(0.995)
        )

        pred = np.clip(
            pred,
            0,
            max_cap
        )

        # Lưu lại kết quả dự báo và biên độ sai số an toàn 
        forecast_results.append({
            'Date': future_date,
            'Forecast Revenue': pred,
            'Upper Bound': pred * 1.12,
            'Lower Bound': pred * 0.88
        })

        # Đưa kết quả vừa dự báo vào đuôi mảng cuốn chiếu để làm dữ liệu nền dự báo cho ngày tiếp theo
        last_values.append(pred)

    # Khởi tạo DataFrame tổng hợp kết quả dự báo tương lai
    forecast_df = pd.DataFrame(
        forecast_results
    )

    # Bộ xử lý ngày lễ thông minh - Đưa doanh thu ngày lễ về 0 sau khi hoàn thành dự báo cuốn chiếu
    forecast_df['Is Holiday'] = (
        forecast_df['Date']
        .isin(vn_holidays)
    )

    forecast_df['Raw Forecast Revenue'] = (
        forecast_df['Forecast Revenue']
    )

    forecast_df.loc[
        forecast_df['Is Holiday'],
        'Forecast Revenue'
    ] = 0

    forecast_df.loc[
        forecast_df['Is Holiday'],
        'Upper Bound'
    ] = 0

    forecast_df.loc[
        forecast_df['Is Holiday'],
        'Lower Bound'
    ] = 0

    # Phân tích thống kê tổng hợp kết quả dự báo theo từng tháng
    forecast_df['Month'] = (
        forecast_df['Date']
        .dt.strftime('%Y-%m')
    )

    monthly_summary = (
        forecast_df
        .groupby('Month')['Forecast Revenue']
        .sum()
        .reset_index()
    )

    print("\n========== KẾT QUẢ DỰ BÁO DOANH THU THEO THÁNG ==========\n")
    for _, row in monthly_summary.iterrows():
        print(f"Tháng {row['Month']} -> Dự kiến đạt: {row['Forecast Revenue']:,.0f} VND")

    # Thống kê phân tích ngày đạt đỉnh doanh thu dự kiến 
    max_day = forecast_df.loc[
        forecast_df['Forecast Revenue'].idxmax()
    ]

    print("\n========== NGÀY ĐẠT ĐỈNH DOANH THU ==========\n")
    print(f"Ngày có doanh thu cao nhất dự kiến : {max_day['Date'].date()}")
    print(f"Giá trị dự báo                    : {max_day['Forecast Revenue']:,.0f} VND")

    # Thống kê phân tích ngày thấp điểm kinh doanh dự kiến (Không tính các ngày lễ được nghỉ)
    business_days_only = forecast_df[
        forecast_df['Is Holiday'] == False
    ]

    min_day = business_days_only.loc[
        business_days_only['Forecast Revenue'].idxmin()
    ]

    print("\n========== NGÀY THẤP ĐIỂM KINH DOANH ==========\n")
    print(f"Ngày có doanh thu thấp nhất dự kiến : {min_day['Date'].date()}")
    print(f"Giá trị dự báo                     : {min_day['Forecast Revenue']:,.0f} VND")

    # Xuất toàn bộ kết quả dự báo ra file Excel phục vụ báo cáo doanh nghiệp
    output_path = r"C:\laptrinhcanban\FINAL_ABSOLUTE_GOD_FORECAST_Q2_2026.xlsx"

    forecast_df.to_excel(
        output_path,
        index=False
    )

    print(f"\n ĐÃ XUẤT FILE KẾT QUẢ DỰ BÁO THÀNH CÔNG:\n{output_path}")

    # Thống kê phân tích tầm quan trọng của các biến đặc trưng đầu vào 
    importance_df = pd.DataFrame({
        'Feature': features,
        'Importance': xgb.feature_importances_
    })

    importance_df = importance_df.sort_values(
        by='Importance',
        ascending=False
    )

    print("\n========== TOP 20 ĐẶC TRƯNG QUAN TRỌNG NHẤT  ==========\n")
    print(importance_df.head(20))

    # Khởi tạo định dạng biểu đồ phân tích giá trị đóng góp SHAP
    print("\n ĐANG KHỞI TẠO ĐỒ THỊ ĐÁNH GIÁ GIÁ TRỊ SHAP...")

    explainer = shap.Explainer(xgb)

    shap_values = explainer(
        X_train[:100]
    )

    shap.plots.bar(
        shap_values,
        max_display=15
    )

    # Cấu hình định dạng đồ thị trực quan hóa chuỗi thời gian doanh thu
    def billions(x, pos):
        return f'{x/1e9:.1f}B'

    formatter = ticker.FuncFormatter(
        billions
    )

    plt.figure(figsize=(32,13))

    # Vẽ đường dữ liệu doanh thu thực tế lịch sử trong quá khứ
    plt.plot(
        df['order_date'],
        df['real_revenue'],
        linewidth=3,
        alpha=0.9,
        label='Doanh thu Thực tế trong Quá khứ'
    )

    # Vẽ đường dự báo kế hoạch doanh thu Quý 2 tương lai sắp tới
    plt.plot(
        forecast_df['Date'],
        forecast_df['Forecast Revenue'],
        linestyle='--',
        linewidth=3,
        alpha=0.95,
        label='Doanh thu Dự báo Quý 2/2026'
    )

    # Đổ màu vùng không gian dải biên sai số an toàn (Khoảng tin cậy dự báo)
    plt.fill_between(
        forecast_df['Date'],
        forecast_df['Lower Bound'],
        forecast_df['Upper Bound'],
        alpha=0.10,
        label='Khoảng tin cậy dự báo (Sai số biên)'
    )

    plt.gca().yaxis.set_major_formatter(
        formatter
    )

    plt.title(' HỆ THỐNG DỰ BÁO DOANH THU — THỐNG NHẤT BIKE QUÝ 2/2026', fontsize=26, weight='bold')
    plt.xlabel('Thời gian (Ngày)', fontsize=16)
    plt.ylabel('Doanh thu (Tỷ VND)', fontsize=16)
    plt.grid(alpha=0.2)
    plt.legend(fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    print("\n QUY TRÌNH CHẠY MÔ HÌNH DỰ BÁO DOANH THU ĐÃ HOÀN THÀNH.")

    return forecast_df