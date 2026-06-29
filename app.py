import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from deep_translator import GoogleTranslator

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Ultimate Stock Analyzer Pro", page_icon="📈", layout="wide")

st.title("📈 Ultimate Stock Analyzer Pro")
st.subheader("ระบบวิเคราะห์การลงทุน 360 องศา (งบการเงิน + มูลค่า + ปัจจัยเชิงคุณภาพ)")
st.markdown("---")

top_50_companies = {
    "AAPL": "Apple Inc. (เทคโนโลยี)", "MSFT": "Microsoft (ซอฟต์แวร์)",
    "GOOGL": "Alphabet Inc. (กูเกิล)", "AMZN": "Amazon (อีคอมเมิร์ซ)",
    "NVDA": "NVIDIA (ชิปประมวลผล)", "META": "Meta Platforms (โซเชียลมีเดีย)",
    "TSLA": "Tesla (ยานยนต์ไฟฟ้า)", "BRK-B": "Berkshire Hathaway (การลงทุน)",
    "LLY": "Eli Lilly (ยาและเวชภัณฑ์)", "V": "Visa (เครือข่ายการชำระเงิน)"
    # (สามารถใส่หุ้น Top 50 ตัวอื่นๆ เพิ่มเติมได้ตามเดิม)
}

st.sidebar.header("🛠️ แผงควบคุม (Control Panel)")
selected_ticker = st.sidebar.selectbox(
    "1. เลือกบริษัทที่ต้องการวิเคราะห์:",
    options=list(top_50_companies.keys()),
    format_func=lambda x: f"{x} - {top_50_companies[x]}"
)

def format_number(num):
    if pd.isna(num) or num is None:
        return "N/A"
    return f"{num:,.2f}"

if st.sidebar.button("🚀 รันระบบวิเคราะห์แบบ 360 องศา"):
    with st.spinner(f"กำลังดึงข้อมูล AI เชิงลึกและแปลภาษาของ {selected_ticker}..."):
        ticker = yf.Ticker(selected_ticker)
        
        # ==========================================
        # ส่วนที่ 1: แถบข้อมูลบริษัท & ราคา (สไตล์ Dashboard มืออาชีพ)
        # ==========================================
        try:
            info = ticker.info
            st.header(f"🏢 {info.get('longName', selected_ticker)} ({selected_ticker})")
            
            # คำนวณการเปลี่ยนแปลงราคา (เพื่อให้มีตัวเลขสีเขียว/แดง เหมือนเว็บ SET)
            current_price = info.get('currentPrice')
            prev_close = info.get('previousClose')
            delta_str = None
            if current_price and prev_close:
                change = current_price - prev_close
                pct_change = (change / prev_close) * 100
                delta_str = f"{change:.2f} ({pct_change:.2f}%)"

            # สร้างแถบข้อมูลด้านบน
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ราคาปัจจุบัน (USD)", f"${format_number(current_price)}", delta_str)
            c2.metric("อุตสาหกรรม", info.get('industry', 'N/A'))
            c3.metric("มาร์เก็ตแคป", f"${format_number(info.get('marketCap', 0) / 1e9)} B")
            c4.metric("P/E Ratio", format_number(info.get('trailingPE')))
            
            # ระบบแปลภาษาอัตโนมัติ
            with st.expander("📖 อ่านรายละเอียดธุรกิจ (Business Summary - แปลไทยอัตโนมัติ)", expanded=True):
                summary_en = info.get('longBusinessSummary', '')
                if summary_en:
                    try:
                        translator = GoogleTranslator(source='auto', target='th')
                        summary_th = translator.translate(summary_en)
                        st.markdown(f"**🇹🇭 ฉบับแปลภาษาไทย:**\n\n{summary_th}")
                        st.markdown("---")
                        st.markdown(f"**🇺🇸 ต้นฉบับ (Original):**\n\n<span style='color:gray'>{summary_en}</span>", unsafe_allow_html=True)
                    except Exception as e:
                        st.write(summary_en)
                        st.caption("(ไม่สามารถแปลภาษาได้ในขณะนี้ กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ต)")
                else:
                    st.write("ไม่มีข้อมูลคำอธิบายธุรกิจในฐานข้อมูล")
        except Exception as e:
            st.warning("⚠️ โหลดข้อมูลโปรไฟล์บริษัทไม่สมบูรณ์")

        st.markdown("---")
        
        # ==========================================
        # ส่วนที่ 2: วิเคราะห์งบการเงิน & คำแนะนำ (Action Plan)
        # ==========================================
        tab1, tab2 = st.tabs(["🕵️‍♂️ เครื่องจับโกหกงบการเงิน (Forensic)", "⚖️ มูลค่าและข้อมูลอื่นๆ"])

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
                        
                        # วาดกราฟ
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=years, y=net_income.values, name='กำไรสุทธิ (Net Income)', marker_color='#1f77b4'))
                        fig.add_trace(go.Bar(x=years, y=cfo.values, name='เงินสดดำเนินงาน (CFO)', marker_color='#2ca02c'))
                        fig.update_layout(barmode='group', title='คุณภาพกำไร: เงินสดของจริง (สีเขียว) ต้องสอดคล้องกับกำไร (สีน้ำเงิน)', height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("### 📋 สรุปผลการวิเคราะห์ และ คำแนะนำ (Action Plan)")
                        flags = 0
                        
                        # 🚩 Flag 1
                        if net_income.iloc[-1] > 0 and cfo.iloc[-1] <= 0:
                            st.error("🚨 **RED FLAG 1: กำไรสุทธิโต แต่กระแสเงินสดดำเนินงานติดลบ**")
                            st.markdown("""
                            > **💡 ความหมาย:** บริษัทรายงานว่ามีกำไร แต่ในความเป็นจริงเก็บเงินสดจากลูกค้าไม่ได้เลย (อาจเกิดจากการเร่งบันทึกรายได้ล่วงหน้า หรือตกแต่งบัญชี)
                            > **🎯 สิ่งที่ควรทำ:** หลีกเลี่ยงการลงทุนชั่วคราว จนกว่าจะเจาะลึกงบกระแสเงินสดว่าเงินจมไปกับอะไร หากจมไปกับ 'ลูกหนี้การค้า' จำนวนมาก ถือว่ามีความเสี่ยงสูง
                            """)
                            flags += 1
                            
                        # 🚩 Flag 2
                        if receivables is not None and revenue is not None:
                            rev_growth, rec_growth = revenue.pct_change().iloc[-1], receivables.pct_change().iloc[-1]
                            if not np.isnan(rec_growth) and not np.isnan(rev_growth) and rec_growth > (rev_growth * 2) and rec_growth > 0.1:
                                st.error(f"🚨 **RED FLAG 2: ลูกหนี้การค้าโตเร็วกว่ายอดขาย (Aggressive Receivables)**")
                                st.markdown(f"""
                                > **💡 ความหมาย:** ยอดขายเติบโต {rev_growth*100:.1f}% แต่การปล่อยเครดิตให้ลูกค้ากู้ยืม (ลูกหนี้) กลับโตถึง {rec_growth*100:.1f}% แปลว่าบริษัทอาจใช้วิธี 'ยัดไส้ยอดขาย' เพื่อให้งบดูดี แต่เสี่ยงเป็นหนี้สูญ
                                > **🎯 สิ่งที่ควรทำ:** ตรวจสอบหมายเหตุประกอบงบการเงินเรื่อง 'อายุลูกหนี้การค้า' ว่ามีลูกหนี้ที่ค้างชำระเกิน 90 วันเพิ่มขึ้นผิดปกติหรือไม่
                                """)
                                flags += 1
                                
                        # ⚠️ Flag 3
                        if inventory is not None and revenue is not None:
                            rev_growth, inv_growth = revenue.pct_change().iloc[-1], inventory.pct_change().iloc[-1]
                            if not np.isnan(inv_growth) and not np.isnan(rev_growth) and inv_growth > 0.05 and rev_growth < 0:
                                st.warning("⚠️ **YELLOW FLAG: สินค้าคงคลังล้นสต็อก สวนทางยอดขาย (Inventory Piling Up)**")
                                st.markdown("""
                                > **💡 ความหมาย:** ยอดขายของบริษัทกำลังลดลง แต่สต็อกสินค้าในโกดังกลับบวมขึ้นเรื่อยๆ 
                                > **🎯 สิ่งที่ควรทำ:** หากบริษัทขายสินค้าเทคโนโลยีหรือแฟชั่น (ที่ตกรุ่นง่าย) ให้ระวังการถูกบันทึกขาดทุนจากการด้อยค่าสินค้าในไตรมาสถัดไป แต่ถ้าเป็นธุรกิจสินค้าโภคภัณฑ์ อาจเป็นแค่การกักตุนสินค้ารอราคาขึ้น
                                """)
                                flags += 1
                                
                        # 🟢 SAFE
                        if flags == 0:
                            st.success("🟢 **GREEN FLAG: งบการเงินเบื้องต้นแข็งแกร่ง ปลอดภัย**")
                            st.markdown("""
                            > **💡 ความหมาย:** ไม่พบความผิดปกติที่ขัดแย้งกันอย่างมีนัยสำคัญระหว่าง กำไรทางบัญชี กับ กระแสเงินสดจริง
                            > **🎯 สิ่งที่ควรทำ:** บริษัทสอบผ่านเกณฑ์คุณภาพงบการเงิน คุณสามารถก้าวไปสู่ขั้นตอนการประเมินมูลค่า (Valuation) ว่าราคาปัจจุบันถูกหรือแพงเกินไปใน Tab ที่ 2 ได้เลย
                            """)
                            
                except Exception as e:
                    st.error("❌ ข้อมูลโครงสร้างบัญชีไม่รองรับการคำนวณ")
            else:
                st.error("❌ ไม่มีข้อมูลย้อนหลังเพียงพอ")

        # แท็บ 2 เป็นข้อมูล Valuation ปกติ
        with tab2:
            st.info("คุณสามารถเพิ่มโค้ดในส่วนของ Valuation และข่าวสารได้เหมือนเวอร์ชันก่อนหน้า")
