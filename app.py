import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. ตั้งค่าหน้าเว็บให้สวยงามสไตล์ Dashboard มืออาชีพ
st.set_page_config(page_title="Ultimate Stock Analyzer Pro", page_icon="📈", layout="wide")

st.title("📈 Ultimate Stock Analyzer Pro")
st.subheader("ระบบวิเคราะห์การลงทุน 360 องศา (งบการเงิน + มูลค่า + ปัจจัยเชิงคุณภาพ)")
st.markdown("---")

# 2. รายชื่อหุ้น Top 50 ของโลก
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

# 3. Sidebar แผงควบคุม
st.sidebar.header("🛠️ แผงควบคุม (Control Panel)")
selected_ticker = st.sidebar.selectbox(
    "1. เลือกบริษัทที่ต้องการวิเคราะห์:",
    options=list(top_50_companies.keys()),
    format_func=lambda x: f"{x} - {top_50_companies[x]}"
)

# ฟังก์ชันแปลงตัวเลขให้ดูง่าย
def format_number(num):
    if pd.isna(num) or num is None:
        return "N/A"
    return f"{num:,.2f}"

if st.sidebar.button("🚀 รันระบบวิเคราะห์แบบ 360 องศา"):
    with st.spinner(f"กำลังดึงข้อมูล AI เชิงลึกของ {selected_ticker} จากฐานข้อมูลโลก..."):
        ticker = yf.Ticker(selected_ticker)
        
        # --- ส่วนที่ 1: ข้อมูลบริษัทเบื้องต้น (Company Profile) ---
        try:
            info = ticker.info
            st.header(f"🏢 {info.get('longName', selected_ticker)} ({selected_ticker})")
            
            # ใช้ st.columns แบ่งข้อมูลเป็นสัดส่วน
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ราคาปัจจุบัน", f"${format_number(info.get('currentPrice'))}")
            c2.metric("อุตสาหกรรม (Industry)", info.get('industry', 'N/A'))
            c3.metric("มาร์เก็ตแคป (Market Cap)", f"${format_number(info.get('marketCap', 0) / 1e9)} B")
            c4.metric("ความเสี่ยง (Beta)", format_number(info.get('beta')))
            
            with st.expander("📖 อ่านรายละเอียดธุรกิจ (Business Summary)"):
                st.write(info.get('longBusinessSummary', 'ไม่มีข้อมูลคำอธิบายธุรกิจในฐานข้อมูล'))
        except Exception as e:
            st.warning("⚠️ โหลดข้อมูลโปรไฟล์บริษัทไม่สมบูรณ์")
            info = {}

        st.markdown("---")
        
        # --- สร้างเมนู Tabs เพื่อความสวยงามและไม่รก ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "🕵️‍♂️ 1. เครื่องจับโกหกงบการเงิน", 
            "⚖️ 2. ประเมินความถูกแพง & คุณภาพ", 
            "🏰 3. ผู้ถือหุ้น & วงใน", 
            "📰 4. ข่าวสาร & ปัจจัยเร่ง"
        ])

        # ==========================================
        # TAB 1: เครื่องจับโกหกงบการเงิน (Forensic)
        # ==========================================
        with tab1:
            st.subheader("ตรวจสอบสัญญาณอันตรายทางบัญชี 5 ปีย้อนหลัง")
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
                        
                        # วาดกราฟ Plotly
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=years, y=net_income.values, name='กำไรสุทธิ (Net Income)', marker_color='#1f77b4'))
                        fig.add_trace(go.Bar(x=years, y=cfo.values, name='เงินสดดำเนินงาน (CFO)', marker_color='#2ca02c'))
                        fig.update_layout(barmode='group', title='คุณภาพกำไร: เงินสดของจริง (สีเขียว) ต้องสอดคล้องกับกำไร (สีน้ำเงิน)', height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # ระบบตรวจจับ (Rule-based)
                        flags = 0
                        if net_income.iloc[-1] > 0 and cfo.iloc[-1] <= 0:
                            st.error(f"🚨 **RED FLAG 1:** กำไรสุทธิโต แต่กระแสเงินสดดำเนินงานติดลบ (ระวังการรับรู้รายได้ปลอม)")
                            flags += 1
                        if receivables is not None and revenue is not None:
                            rev_growth, rec_growth = revenue.pct_change().iloc[-1], receivables.pct_change().iloc[-1]
                            if not np.isnan(rec_growth) and not np.isnan(rev_growth) and rec_growth > (rev_growth * 2) and rec_growth > 0.1:
                                st.error(f"🚨 **RED FLAG 2:** ลูกหนี้การค้าโตเร็วกว่ายอดขาย (Aggressive Receivables)")
                                flags += 1
                        if inventory is not None and revenue is not None:
                            rev_growth, inv_growth = revenue.pct_change().iloc[-1], inventory.pct_change().iloc[-1]
                            if not np.isnan(inv_growth) and not np.isnan(rev_growth) and inv_growth > 0.05 and rev_growth < 0:
                                st.warning(f"⚠️ **WARNING:** สินค้าคงคลังล้นสต็อก สวนทางยอดขายที่ลดลง (Inventory Piling Up)")
                                flags += 1
                        if flags == 0:
                            st.success("🟢 **สอบผ่าน:** งบการเงินปลอดภัย ไม่พบสัญญาณตกแต่งบัญชีเบื้องต้น")
                except Exception as e:
                    st.error("❌ ข้อมูลโครงสร้างบัญชีไม่รองรับการคำนวณ")
            else:
                st.error("❌ ไม่มีข้อมูลย้อนหลังเพียงพอ")

        # ==========================================
        # TAB 2: มูลค่า & ความสามารถทำกำไร (Valuation & Moat)
        # ==========================================
        with tab2:
            st.subheader("ประเมินราคาหุ้น และความได้เปรียบทางการแข่งขัน")
            
            st.markdown("##### ⚖️ อัตราส่วนความถูกแพง (Valuation Metrics)")
            v1, v2, v3, v4 = st.columns(4)
            v1.metric("P/E Ratio (ราคา/กำไร)", format_number(info.get('trailingPE')), help="กี่ปีคืนทุน ถ้ายิ่งต่ำยิ่งถูก")
            v2.metric("Forward P/E", format_number(info.get('forwardPE')), help="P/E ที่คาดการณ์ในปีหน้า")
            v3.metric("PEG Ratio", format_number(info.get('pegRatio')), help="P/E หารด้วยการเติบโต (ต่ำกว่า 1 คือถูก)")
            v4.metric("Price / Book", format_number(info.get('priceToBook')), help="ราคาเทียบกับมูลค่าทางบัญชี")

            st.markdown("##### 🏰 ความสามารถในการทำกำไร (Profitability & Moat)")
            st.info("💡 ข้อสังเกต: บริษัทที่มีอำนาจผูกขาด หรือมีแบรนด์ที่แข็งแกร่ง (Moat) มักจะมีอัตรากำไร (Margin) ที่สูงลิ่ว")
            
            p1, p2, p3 = st.columns(3)
            # ข้อมูล margin มาเป็นทศนิยม (เช่น 0.25 คือ 25%) เราจึงคูณ 100
            gross_margin = info.get('grossMargins', 0) * 100 if info.get('grossMargins') else None
            op_margin = info.get('operatingMargins', 0) * 100 if info.get('operatingMargins') else None
            net_margin = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None
            
            p1.metric("Gross Margin (กำไรขั้นต้น)", f"{format_number(gross_margin)} %")
            p2.metric("Operating Margin (กำไรจากการดำเนินงาน)", f"{format_number(op_margin)} %")
            p3.metric("Net Profit Margin (กำไรสุทธิ)", f"{format_number(net_margin)} %")

        # ==========================================
        # TAB 3: โครงสร้างผู้ถือหุ้น (Ownership)
        # ==========================================
        with tab3:
            st.subheader("ใครคือเจ้าของตัวจริง? (Institutional & Insider)")
            
            st.markdown("##### กองทุนสถาบันที่ถือหุ้นใหญ่")
            try:
                inst_holders = ticker.institutional_holders
                if inst_holders is not None and not inst_holders.empty:
                    # จัดหน้าตาตารางให้สวย
                    inst_holders.columns = ['ผู้ถือหุ้นสถาบัน (Holder)', 'จำนวนหุ้น (Shares)', 'วันที่รายงาน', '% ถือครอง', 'มูลค่า (USD)']
                    st.dataframe(inst_holders[['ผู้ถือหุ้นสถาบัน (Holder)', 'จำนวนหุ้น (Shares)', '% ถือครอง']], use_container_width=True)
                else:
                    st.write("ไม่พบข้อมูลผู้ถือหุ้นสถาบัน")
            except:
                st.write("ข้อมูลผู้ถือหุ้นสถาบันไม่พร้อมใช้งาน")

        # ==========================================
        # TAB 4: ข่าวสาร & ปัจจัยเร่ง (News)
        # ==========================================
        with tab4:
            st.subheader("📰 ข่าวล่าสุด (Catalysts & Sentiment)")
            try:
                news = ticker.news
                if news:
                    for article in news[:5]: # ดึงมา 5 ข่าวล่าสุด
                        with st.container():
                            st.markdown(f"**[{article['title']}]({article['link']})**")
                            st.caption(f"สำนักข่าว: {article['publisher']} | รหัสข่าว: {article['uuid']}")
                            st.divider()
                else:
                    st.write("ไม่มีข่าวอัปเดตในช่วงนี้")
            except:
                st.write("ไม่สามารถดึงข้อมูลข่าวสารได้")

else:
    # หน้าจอตอนที่ยังไม่ได้กดรัน
    st.info("👈 กรุณาเลือกชื่อบริษัทจากแถบด้านซ้าย แล้วกดปุ่ม 'รันระบบวิเคราะห์แบบ 360 องศา'")
    st.image("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&q=80&w=1200", caption="Invest with Data, Not Emotions.")
