import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Forensic Accounting Screener Pro", page_icon="🕵️‍♂️", layout="wide")

st.title("🕵️‍♂️ Forensic Accounting Screener Pro")
st.subheader("ระบบวิเคราะห์และจับโกหกงบการเงินอัตโนมัติ (Top 50 Global Companies)")
st.markdown("---")

top_50_companies = {
    "AAPL": "Apple Inc. (เทคโนโลยี)", "MSFT": "Microsoft (ซอฟต์แวร์/คลาวด์)",
    "GOOGL": "Alphabet Inc. (กูเกิล)", "AMZN": "Amazon (อีคอมเมิร์ซ/คลาวด์)",
    "NVDA": "NVIDIA (ชิปประมวลผล/AI)", "META": "Meta Platforms (โซเชียลมีเดีย)",
    "TSLA": "Tesla (ยานยนต์ไฟฟ้า)", "BRK-B": "Berkshire Hathaway (การลงทุน)",
    "LLY": "Eli Lilly (ยาและเวชภัณฑ์)", "AVGO": "Broadcom (เซมิคอนดักเตอร์)",
    "V": "Visa (เครือข่ายการชำระเงิน)", "MA": "Mastercard (เครือข่ายการชำระเงิน)",
    "JPM": "JPMorgan Chase (ธนาคาร)", "UNH": "UnitedHealth Group (ประกันสุขภาพ)",
    "WMT": "Walmart (ค้าปลีก)", "XOM": "Exxon Mobil (พลังงาน)",
    "PG": "Procter & Gamble (สินค้าอุปโภคบริโภค)", "JNJ": "Johnson & Johnson (สินค้าสุขภาพ)",
    "HD": "Home Depot (วัสดุก่อสร้าง)", "ORCL": "Oracle (ระบบฐานข้อมูล)",
    "COST": "Costco (ห้างค้าส่ง)", "MRK": "Merck & Co. (ยาและชีวเภสัชภัณฑ์)",
    "CVX": "Chevron (พลังงาน)", "BAC": "Bank of America (ธนาคาร)",
    "NFLX": "Netflix (สตรีมมิ่ง)", "AMD": "AMD (ชิปประมวลผล)",
    "KO": "Coca-Cola (เครื่องดื่ม)", "PEP": "PepsiCo (เครื่องดื่มและขนม)",
    "ADBE": "Adobe (ซอฟต์แวร์สร้างสรรค์)", "TSM": "TSMC (โรงงานผลิตชิป)",
    "ASML": "ASML Holding (เครื่องจักรผลิตเซมิคอนดักเตอร์)", "NVO": "Novo Nordisk (ยา)",
    "CRM": "Salesforce (ซอฟต์แวร์)", "DIS": "Walt Disney (สื่อและความบันเทิง)",
    "CSCO": "Cisco (อุปกรณ์เครือข่าย)", "TM": "Toyota (ยานยนต์)",
    "NKE": "NIKE (อุปกรณ์กีฬา)", "PFE": "Pfizer (ยาและวัคซีน)",
    "INTC": "Intel (ชิปประมวลผล)", "CMCSA": "Comcast (สื่อและโทรคมนาคม)",
    "VZ": "Verizon (โทรคมนาคม)", "T": "AT&T (โทรคมนาคม)",
    "IBM": "IBM (ไอทีเทคโนโลยี)", "TXN": "Texas Instruments (เซมิคอนดักเตอร์)",
    "QCOM": "QUALCOMM (ชิปสื่อสาร)", "HON": "Honeywell (อุตสาหกรรมเทคโนโลยี)",
    "GE": "General Electric (อุตสาหกรรม)", "BA": "Boeing (อากาศยาน)",
    "CAT": "Caterpillar (เครื่องจักรกลหนัก)", "AXP": "American Express (บริการการเงิน)"
}

st.sidebar.header("🛠️ ส่วนควบคุมการค้นหา")
selected_ticker = st.sidebar.selectbox(
    "เลือกบริษัทที่ต้องการสแกนงบ:",
    options=list(top_50_companies.keys()),
    format_func=lambda x: f"{x} - {top_50_companies[x]}"
)

if st.sidebar.button("🚀 เริ่มการวิเคราะห์เชิงลึก"):
    with st.spinner(f"🕵️‍♂️ กำลังตรวจสอบบัญชีย้อนหลัง 5 ปีของ {selected_ticker}..."):
        ticker = yf.Ticker(selected_ticker)
        
        try:
            info = ticker.info
            st.subheader(f"🏢 ข้อมูลบริษัท: {info.get('longName', selected_ticker)}")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric(label="หมวดหมู่อุตสาหกรรม", value=info.get('industry', 'ไม่ระบุ'))
            with col2:
                st.write(info.get('longBusinessSummary', 'ไม่มีข้อมูลคำอธิบายธุรกิจในฐานข้อมูล')[:300] + "...")
        except:
            st.warning("⚠️ ไม่สามารถดึงข้อมูลประวัติบริษัทได้")
            
        st.markdown("---")
        
        inc = ticker.financials
        cf = ticker.cashflow
        bal = ticker.balance_sheet
        
        if not inc.empty and not cf.empty and not bal.empty:
            try:
                net_income = inc.loc['Net Income'].iloc[::-1] if 'Net Income' in inc.index else None
                revenue = inc.loc['Total Revenue'].iloc[::-1] if 'Total Revenue' in inc.index else None
                cfo_name = 'Operating Cash Flow' if 'Operating Cash Flow' in cf.index else ( 'Total Cash From Operating Activities' if 'Total Cash From Operating Activities' in cf.index else None)
                cfo = cf.loc[cfo_name].iloc[::-1] if cfo_name else None
                rec_name = 'Accounts Receivable' if 'Accounts Receivable' in bal.index else ('Net Receivables' if 'Net Receivables' in bal.index else None)
                receivables = bal.loc[rec_name].iloc[::-1] if rec_name else None
                inventory = bal.loc['Inventory'].iloc[::-1] if 'Inventory' in bal.index else None
                
                if net_income is not None and cfo is not None:
                    years = [str(year)[:4] for year in net_income.index]
                    
                    st.subheader(f"📊 กราฟเปรียบเทียบคุณภาพกำไร ({selected_ticker})")
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=years, y=net_income.values, name='กำไรสุทธิ (Net Income)', marker_color='#1f77b4'))
                    fig.add_trace(go.Bar(x=years, y=cfo.values, name='เงินสดดำเนินงาน (CFO)', marker_color='#2ca02c'))
                    fig.update_layout(barmode='group', title='แท่งเงินสด (สีเขียว) ควรล้อไปกับแท่งกำไร (สีน้ำเงิน) และไม่ควรติดลบ 🚩')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader("🕵️‍♂️ ผลการตรวจสอบสัญญาณอันตราย (Red Flags)")
                    flags = 0
                    
                    if net_income.iloc[-1] > 0 and cfo.iloc[-1] <= 0:
                        st.error(f"🚨 **RED FLAG 1:** กำไรโต แต่เงินสดติดลบ (ระวังการรับรู้รายได้ปลอม)")
                        flags += 1
                        
                    if receivables is not None and revenue is not None:
                        rev_growth, rec_growth = revenue.pct_change().iloc[-1], receivables.pct_change().iloc[-1]
                        if not np.isnan(rec_growth) and not np.isnan(rev_growth) and rec_growth > (rev_growth * 2) and rec_growth > 0.1:
                            st.error(f"🚨 **RED FLAG 2:** ลูกหนี้การค้าโตเร็วกว่ายอดขาย (Aggressive Receivables)")
                            flags += 1
                            
                    if inventory is not None and revenue is not None:
                        rev_growth, inv_growth = revenue.pct_change().iloc[-1], inventory.pct_change().iloc[-1]
                        if not np.isnan(inv_growth) and not np.isnan(rev_growth) and inv_growth > 0.05 and rev_growth < 0:
                            st.warning(f"⚠️ **WARNING:** สินค้าคงคลังล้นสต็อก สวนทางกับยอดขาย (Inventory Piling Up)")
                            flags += 1
                                
                    if flags == 0:
                        st.success("🟢 **งบการเงินปลอดภัย:** ไม่พบสัญญาณอันตรายใดๆ ในรอบปีล่าสุด")
                        
            except Exception as ex:
                st.error(f"❌ เกิดข้อผิดพลาดในการคำนวณ: {str(ex)}")
        else:
            st.error("❌ โครงสร้างงบการเงินไม่สมบูรณ์")
else:
    st.info("👈 เลือกบริษัทจากเมนูด้านซ้าย แล้วกดปุ่มเริ่มวิเคราะห์")
