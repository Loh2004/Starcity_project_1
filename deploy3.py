import base64
import os
import io
import re
import numpy as np
import pandas as pd
import streamlit as st

# --- 1. PAGE SETUP (Must be first Streamlit command) ---
st.set_page_config(
    page_title="Star City | Smart Quote Matrix",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ASSET HELPERS & ULTRA-PREMIUM THEME CSS ---
def get_base64_of_image(file_path):
    """Encodes a local image to base64 format safely."""
    if os.path.exists(file_path):
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

LOGO_FILENAME = "logo_star.png"
base64_img = get_base64_of_image(LOGO_FILENAME)

custom_bg_style = ""
if base64_img:
    custom_bg_style = f"""
        background-color: #f1f5f9;
        background-image: linear-gradient(135deg, rgba(248, 250, 252, 0.45) 0%, rgba(241, 245, 249, 0.45) 100%), 
                          url("data:image/png;base64,{base64_img}");
        background-size: min(720px, 80vw) auto;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    """
else:
    custom_bg_style = "background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0f172a;
        {custom_bg_style}
    }}

    /* Main Container Padding */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1350px;
    }}

    /* Glassmorphism on Hero & Cards for perfect legibility over prominent logo */
    .hero-container {{
        background: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.9);
        box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
    }}
    .kpi-card {{
        background: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.9);
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .content-card {{
        background: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.9);
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
        margin-bottom: 24px;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: #f8fafc !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stNumberInput label {{
        font-weight: 600;
        font-size: 0.88rem;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        color: #94a3b8 !important;
    }}

    /* Hero Banner */
    .hero-title {{
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .hero-subtitle {{
        font-size: 0.95rem;
        color: #475569;
        margin-top: 6px;
        margin-bottom: 0;
        font-weight: 500;
    }}
    .brand-pill {{
        background: #eff6ff;
        color: #1d4ed8;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        border: 1px solid #dbeafe;
        display: inline-block;
    }}

    /* KPI Metric Cards Grid */
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 24px -6px rgba(15, 23, 42, 0.12);
    }}
    .kpi-label {{
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }}
    .kpi-value {{
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }}
    .kpi-meta {{
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 6px;
        font-weight: 600;
    }}
    .kpi-value.accent-green {{
        color: #059669;
    }}
    .kpi-value.accent-blue {{
        color: #2563eb;
    }}

    /* Section Headings */
    .section-header {{
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }}

    /* Styled Buttons */
    .stDownloadButton button {{
        background: #0f172a !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.4rem !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }}
    .stDownloadButton button:hover {{
        background: #1e293b !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.25) !important;
    }}

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #64748b;
        border: none !important;
        background: transparent;
    }}
    .stTabs [aria-selected="true"] {{
        background: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
    }}

    /* Table Container Styling */
    [data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. HELPER FUNCTIONS ---
def round_up_to_two_decimals(values):
    """Round positive numeric values upward to two decimal places."""
    return np.ceil(values * 100) / 100

def clean_part_string(val):
    """Safely normalizes part number strings and strips trailing .0 float conversions."""
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if s.endswith('.0'):
        s = s[:-2]
    if s.lower() in ['nan', 'null', 'none', '#n/a', '0', '']:
        return ""
    return s

def clean_numeric(val):
    """Strips currency symbols, commas, and extracts valid float numbers."""
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s.lower() in ['#n/a', 'nan', 'none', 'null', '-', '']:
        return np.nan
    s_cleaned = re.sub(r'[^\d.-]', '', s)
    try:
        return float(s_cleaned)
    except (ValueError, TypeError):
        return np.nan

def make_columns_unique(cols):
    """Ensures all column names are unique and valid strings for Pandas Styler."""
    seen = {}
    unique_cols = []
    for i, col in enumerate(cols):
        c_str = str(col).strip()
        if not c_str or c_str.lower() in ['nan', 'none', 'unnamed']:
            c_str = f"Column_{i+1}"
        if c_str in seen:
            seen[c_str] += 1
            unique_cols.append(f"{c_str}_{seen[c_str]}")
        else:
            seen[c_str] = 0
            unique_cols.append(c_str)
    return unique_cols

# --- 4. SIDEBAR CONFIGURATION ---
sidebar_logo_html = f'<img src="data:image/png;base64,{base64_img}" style="max-height: 42px; object-fit: contain;" />' if base64_img else '<span style="font-size: 1.6rem;">🚗</span>'

st.sidebar.markdown(
    f"""
    <div style="margin-bottom: 20px; display: flex; align-items: center; gap: 12px;">
        {sidebar_logo_html}
        <div>
            <span style="font-size: 1.25rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">Star City</span>
            <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">Quote Visualizer</p>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

default_aed_rates = {
    "AED": 1.0000,
    "USD": 0.2723,    # 1 AED = 0.2723 USD (1 USD ~ 3.6725 AED)
    "EUR": 0.2500,    # 1 AED ~ 0.2500 EUR
    "SAR": 1.0210,    # 1 AED ~ 1.0210 SAR
    "GBP": 0.2150,    # 1 AED ~ 0.2150 GBP
    "INR": 22.7500,   # 1 AED ~ 22.7500 INR
    "JPY": 43.3800    # 1 AED ~ 43.3800 JPY
}

target_currency = st.sidebar.selectbox(
    "Target Quote Currency", 
    list(default_aed_rates.keys()), 
    index=0,
    help="Master sheet input is in AED. Select the currency you want to quote to the customer."
)
suggested_rate = default_aed_rates.get(target_currency, 1.0000)

if target_currency == "AED":
    conversion_rate = 1.0000
    st.sidebar.caption("🔒 Base Rate: 1 AED = 1.0000 AED")
else:
    conversion_rate = st.sidebar.number_input(
        f"Exchange Rate (1 AED = ? {target_currency})",
        min_value=0.0001,
        value=float(suggested_rate),
        format="%.4f",
        help="Adjust exchange rate multiplier from AED base"
    )

margin = st.sidebar.number_input(
    "Profit Markup (%)", 
    min_value=0.0, 
    max_value=500.0, 
    value=15.0, 
    step=0.5,
    help="Calculates Selling Price = Converted Cost × (1 + Margin/100)"
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="background: rgba(255, 255, 255, 0.05); padding: 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1);">
        <p style="font-size: 0.78rem; color: #94a3b8; margin: 0; line-height: 1.5;">
            💡 <b>Pricing Rule:</b> Automatically isolates the lowest-cost supplier per part, fulfills partial quantities across vendors, and rounds up to 2 decimal places.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 5. MAIN HEADER HERO ---
hero_logo_html = f'<img src="data:image/png;base64,{base64_img}" style="max-height: 72px; object-fit: contain; border-radius: 8px;" alt="Logo" />' if base64_img else ''

st.markdown(
    f"""
    <div class="hero-container">
        <div>
            <span class="brand-pill">Automotive Spare Parts Trading</span>
            <h1 class="hero-title">Star City Auto Spare Parts Trading L.L.C.</h1>
            <p class="hero-subtitle">Intelligent multi-supplier master list analysis, lowest-cost optimization & instant quotation generator.</p>
        </div>
        {hero_logo_html}
    </div>
    """, 
    unsafe_allow_html=True
)

# --- 6. FILE UPLOAD WORKSPACE ---
matrix_file = st.file_uploader(
    "📤 Drop your Consolidated Master Sheet (Excel or CSV)", 
    type=["xlsx", "xls", "csv"], 
    key="single_matrix",
    help="Upload your vertical multi-supplier sheet with columns: si, Part No., Description, QTY, Now_available, NSP, cust_name."
)

if not matrix_file:
    # Empty State - High-end Guidance Card
    st.markdown(
        """
        <div class="content-card" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">📂</div>
            <h3 style="font-size: 1.25rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">Ready to generate optimal quotes?</h3>
            <p style="font-size: 0.92rem; color: #64748b; max-width: 540px; margin: 0 auto 20px auto;">
                Upload your supplier matrix above to automatically match part numbers, pick the best supplier rates, and export clean client-ready quotations.
            </p>
            <div style="display: inline-flex; gap: 24px; text-align: left; background: #f8fafc; padding: 14px 20px; border-radius: 12px; border: 1px solid #e2e8f0;">
                <div><span style="font-weight: 700; color: #0f172a;">✔ Multi-Vendor Pooling</span><br><span style="font-size: 0.78rem; color: #64748b;">Splits quantities across best prices</span></div>
                <div><span style="font-weight: 700; color: #0f172a;">✔ AED Currency Engine</span><br><span style="font-size: 0.78rem; color: #64748b;">Seamless conversion & margin markup</span></div>
                <div><span style="font-weight: 700; color: #0f172a;">✔ Excel & CSV Export</span><br><span style="font-size: 0.78rem; color: #64748b;">Formatted tables with 1-click download</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    file_ext = os.path.splitext(matrix_file.name)[1].lower()
    try:
        if file_ext == '.csv':
            df_raw = pd.read_csv(matrix_file, header=None, dtype=str)
        else:
            df_raw = pd.read_excel(matrix_file, header=None, dtype=str)
    except Exception as e:
        st.error(f"❌ Error parsing uploaded file: {e}")
        st.stop()
    
    # 1. Dynamically locate header row matching your keys
    header_row_idx = None
    for idx, row in df_raw.iterrows():
        row_str = [str(x).lower().strip() for x in row.values]
        if any(keyword in cell for cell in row_str for keyword in ['part no', 'part_no', 'part number', 'part #', 'item code']):
            header_row_idx = idx
            break
            
    if header_row_idx is None:
        st.error("⚠️ Could not detect the header row containing 'Part No.'. Please verify your file structure.")
    else:
        raw_headers = df_raw.iloc[header_row_idx].fillna("").astype(str).str.strip().values
        headers_lower = [h.lower() for h in raw_headers]
        
        # Column detection with exact & substring mappings
        si_idx = next((i for i, h in enumerate(headers_lower) if h in ['si', 's.no', 'sl', 'sl no', 'item', 'item no', 'sr no', 's/n', 's.n']), None)
        alt_idx = next((i for i, h in enumerate(headers_lower) if any(k in h for k in ['alternate', 'alt', 's/s'])), None)
        part_idx = next((i for i, h in enumerate(headers_lower) if 'part' in h and i != alt_idx), None)
        desc_idx = next((i for i, h in enumerate(headers_lower) if 'desc' in h), None)
        qty_idx = next((i for i, h in enumerate(headers_lower) if 'qty' in h or 'quantity' in h), None)
        stk_idx = next((i for i, h in enumerate(headers_lower) if any(k in h for k in ['now_available', 'now', 'avail', 'stk', 'stock'])), None)
        cost_idx = next((i for i, h in enumerate(headers_lower) if any(k in h for k in ['nsp', 'price', 'cost', 'rate'])), None)
        sup_idx = next((i for i, h in enumerate(headers_lower) if any(k in h for k in ['cust_name', 'sup', 'vendor', 'supplier'])), None)
        
        if None in [part_idx, stk_idx, cost_idx]:
            missing = []
            if part_idx is None: missing.append("Part No.")
            if stk_idx is None: missing.append("Now_available / Stock")
            if cost_idx is None: missing.append("NSP / Price")
            st.error(f"⚠️ Column matching error. Missing required columns: **{', '.join(missing)}**.")
            st.info(f"Headers found at row {header_row_idx + 1}: `{list(raw_headers)}`")
        else:
            data_df = df_raw.iloc[header_row_idx + 1:].copy()
            
            # 2. Build Multi-Supplier Catalog Pool (Grouped strictly by Customer Request Line / Normalized Part)
            catalog = {}
            for r_idx, row in data_df.iterrows():
                part = clean_part_string(row.iloc[part_idx])
                if not part:
                    continue
                
                # Check Serial / Item number (e.g. 1 to 147)
                si_raw = clean_numeric(row.iloc[si_idx]) if si_idx is not None else np.nan
                si_val = int(si_raw) if not np.isnan(si_raw) and si_raw > 0 else None
                
                # Group key: Priority to customer line item 'si' (1 to 147), fallback to normalized alphanumeric part
                item_key = si_val if si_val is not None else re.sub(r'[^a-zA-Z0-9]', '', part).upper()
                
                alt_part = clean_part_string(row.iloc[alt_idx]) if alt_idx is not None else ""
                
                desc_val = str(row.iloc[desc_idx]).strip() if desc_idx is not None and not pd.isna(row.iloc[desc_idx]) else ""
                desc_val = "" if desc_val.lower() in ['#n/a', 'nan', 'none', 'null', 'no records found'] else desc_val
                
                qty_raw = clean_numeric(row.iloc[qty_idx]) if qty_idx is not None else 0
                qty_req = int(qty_raw) if not np.isnan(qty_raw) and qty_raw > 0 else 0
                
                supplier = str(row.iloc[sup_idx]).strip() if sup_idx is not None and not pd.isna(row.iloc[sup_idx]) else "Unknown"
                supplier = "Unknown" if supplier.lower() in ['#n/a', 'nan', 'none'] else supplier

                stk_raw = clean_numeric(row.iloc[stk_idx])
                stk_val = int(stk_raw) if not np.isnan(stk_raw) and stk_raw > 0 else 0
                
                cost_val = clean_numeric(row.iloc[cost_idx])

                if item_key not in catalog:
                    catalog[item_key] = {
                        'part_no': part,
                        'max_qty_requested': qty_req,
                        'fallback_ss': alt_part,
                        'fallback_desc': desc_val,
                        'options': []
                    }
                else:
                    # Update part name if current one is cleaner or previous was empty
                    if part and (not catalog[item_key]['part_no'] or catalog[item_key]['part_no'].lower() in ['#n/a', 'nan']):
                        catalog[item_key]['part_no'] = part
                    if qty_req > catalog[item_key]['max_qty_requested']:
                        catalog[item_key]['max_qty_requested'] = qty_req
                    if alt_part and not catalog[item_key]['fallback_ss']:
                        catalog[item_key]['fallback_ss'] = alt_part
                    if desc_val and not catalog[item_key]['fallback_desc']:
                        catalog[item_key]['fallback_desc'] = desc_val

                # Record valid supplier quotation options (stock > 0 and cost > 0)
                if stk_val > 0 and not np.isnan(cost_val) and cost_val > 0:
                    catalog[item_key]['options'].append({
                        'cost': float(cost_val),
                        'stock': stk_val,
                        'supplier': supplier,
                        'original_df_row_idx': r_idx
                    })

            # 3. Calculate Consolidated Pricing (Preserving exact 1-147 order)
            final_rows = []
            serial_no = 1
            winning_row_indices = set()
            
            # Sort items by customer request order (e.g. 1 to 147)
            sorted_catalog_items = sorted(
                catalog.items(), 
                key=lambda x: (0, x[0]) if isinstance(x[0], int) else (1, str(x[0]))
            )
            
            for item_key, item_data in sorted_catalog_items:
                part = item_data['part_no']
                qty_needed = item_data['max_qty_requested']
                effective_qty = qty_needed if qty_needed > 0 else 1
                
                # Sort suppliers by lowest cost first
                sorted_options = sorted(item_data['options'], key=lambda x: x['cost'])
                
                if sorted_options:
                    winning_row_indices.add(sorted_options[0]['original_df_row_idx'])
                    
                remaining_qty = effective_qty
                total_fulfilled_qty = 0
                total_blended_cost_pool = 0.0
                selected_suppliers = []
                
                for opt in sorted_options:
                    if remaining_qty <= 0:
                        break
                    take_qty = min(remaining_qty, opt['stock'])
                    if take_qty <= 0:
                        continue
                    
                    total_fulfilled_qty += take_qty
                    total_blended_cost_pool += (opt['cost'] * take_qty)
                    selected_suppliers.append(f"{opt['supplier']} ({take_qty})")
                    remaining_qty -= take_qty
                    
                final_unit_price = 0.0
                final_total_price = 0.0
                
                if total_fulfilled_qty > 0:
                    avg_unit_cost_aed = total_blended_cost_pool / total_fulfilled_qty
                    # 1. Convert AED Base Cost to Target Currency
                    avg_unit_cost_target = avg_unit_cost_aed * conversion_rate
                    # 2. Markup formula: Selling Price = Converted Cost * (1 + Margin%)
                    selling_price = avg_unit_cost_target * (1.0 + (margin / 100.0))
                    final_unit_price = round_up_to_two_decimals(selling_price)
                    final_total_price = round_up_to_two_decimals(final_unit_price * total_fulfilled_qty)
                    
                # Fulfillment Status
                if total_fulfilled_qty == 0:
                    status_text = "❌ Out of Stock"
                elif total_fulfilled_qty < qty_needed:
                    status_text = f"⚠️ Partial ({total_fulfilled_qty}/{qty_needed})"
                else:
                    status_text = "✅ In Stock"

                s_no_display = item_key if isinstance(item_key, int) else serial_no
                col_unit_price = f"UNIT PRICE {target_currency}"
                col_total_price = f"TOTAL PRICE {target_currency}"

                final_rows.append({
                    "SI NO": s_no_display,
                    "PART NUMBER": part,
                    "S/S": item_data['fallback_ss'] if item_data['fallback_ss'] else "",
                    "DESCRIPTION": item_data['fallback_desc'],
                    "QTY": qty_needed,
                    "STK": total_fulfilled_qty,
                    col_unit_price: float(final_unit_price),
                    col_total_price: float(final_total_price)
                })
                serial_no += 1

            df_quote = pd.DataFrame(final_rows)

            if df_quote.empty:
                st.warning("⚠️ No valid parts found in the uploaded file.")
            else:
                col_unit_price = f"UNIT PRICE {target_currency}"
                col_total_price = f"TOTAL PRICE {target_currency}"

                # --- 7. ULTRA-CLEAN KPI METRIC CARDS ---
                total_parts = len(df_quote)
                in_stock_parts = len(df_quote[df_quote["STK"] > 0])
                fulfillment_rate = (in_stock_parts / total_parts * 100) if total_parts > 0 else 0
                total_val = df_quote[col_total_price].sum()

                st.markdown(
                    f"""
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-label">📦 Unique Parts Analyzed</div>
                            <div class="kpi-value">{total_parts}</div>
                            <div class="kpi-meta">Catalog items detected</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-label">⚡ Stock Availability</div>
                            <div class="kpi-value accent-green">{in_stock_parts} <span style="font-size: 1.1rem; color: #64748b; font-weight: 500;">/ {total_parts}</span></div>
                            <div class="kpi-meta">{fulfillment_rate:.1f}% fulfillment rate</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-label">💰 Total Quote Value ({target_currency})</div>
                            <div class="kpi-value accent-blue">{total_val:,.2f}</div>
                            <div class="kpi-meta">Markup applied: +{margin}%</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-label">💱 Currency Mode</div>
                            <div class="kpi-value">{target_currency}</div>
                            <div class="kpi-meta">Rate: 1 AED = {conversion_rate:.4f} {target_currency}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # --- 8. TABS FOR CLEAN WORKFLOW NAVIGATION ---
                tab_quote, tab_master = st.tabs(["📊 Consolidated Quote Matrix", "🔍 Master List Inspector (Best Prices Highlighted)"])

                with tab_quote:
                    # Filter Controls
                    col_f1, col_f2 = st.columns([2, 1])
                    with col_f1:
                        filter_status = st.radio(
                            "Filter by Availability:",
                            ["All Parts", "✅ In Stock Only", "❌ Out of Stock Only"],
                            horizontal=True
                        )
                    
                    df_filtered = df_quote.copy()
                    if filter_status == "✅ In Stock Only":
                        df_filtered = df_filtered[df_filtered["STK"] > 0]
                    elif filter_status == "❌ Out of Stock Only":
                        df_filtered = df_filtered[df_filtered["STK"] == 0]

                    st.dataframe(
                        df_filtered.style.format({
                            col_unit_price: "{:,.2f}",
                            col_total_price: "{:,.2f}"
                        }),
                        use_container_width=True,
                        height=420
                    )

                    # Export Section
                    st.markdown("#### 💾 Export Client Quotation")
                    col_d1, col_d2 = st.columns(2)
                    
                    csv_bytes = df_quote.to_csv(index=False).encode('utf-8')
                    col_d1.download_button(
                        label="📥 Download Quote as CSV",
                        data=csv_bytes,
                        file_name="Star_City_Quote_Matrix.csv",
                        mime="text/csv",
                        key="btn_download_csv"
                    )

                    excel_buffer = io.BytesIO()
                    excel_ready = False
                    for engine_name in ['openpyxl', 'xlsxwriter']:
                        try:
                            with pd.ExcelWriter(excel_buffer, engine=engine_name) as writer:
                                df_quote.to_excel(writer, index=False, sheet_name='Quote Matrix')
                            excel_ready = True
                            break
                        except Exception:
                            excel_buffer = io.BytesIO()
                            continue

                    if excel_ready:
                        col_d2.download_button(
                            label="📥 Download Quote as Excel (.xlsx)",
                            data=excel_buffer.getvalue(),
                            file_name="Star_City_Quote_Matrix.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="btn_download_excel"
                        )
                    else:
                        col_d2.info("💡 Note: Run `pip install openpyxl` to enable Excel (.xlsx) downloads.")

                with tab_master:
                    st.markdown(
                        """
                        <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 12px;">
                            The master list below highlights in <b style="color: #059669;">green</b> the winning supplier rows that offered the lowest available cost for each part.
                        </p>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    preview_df = data_df.copy()
                    preview_df.columns = make_columns_unique(raw_headers)

                    def highlight_winning_rows(row):
                        if row.name in winning_row_indices:
                            return ['background-color: #dcfce7; color: #166534; font-weight: 600;'] * len(row)
                        return [''] * len(row)

                    try:
                        styled_preview = preview_df.head(250).style.apply(highlight_winning_rows, axis=1)
                        st.dataframe(styled_preview, use_container_width=True, height=450)
                    except Exception:
                        st.dataframe(preview_df.head(250), use_container_width=True, height=450)