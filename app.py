import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from deep_translator import GoogleTranslator

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Ultimate Stock Analyzer Pro", page_icon="📈", layout="wide")

# --- CSS ตกแต่งให้เหมือนเว็บ SET ---
st.markdown("""
<style>
    .set-banner {
        background: linear-gradient(180deg, #4b4b4b 0%, #2b2b2b 100%);
        padding: 20px 30px;
        border-radius: 8px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .set-ticker { font-size: 32px; font-weight: bold; margin: 0; line-height: 1; }
    .set-name { font-size: 16px; color: #cccccc; margin: 5px 0 0 0; }
    .set-price-box { text-align: right; }
    .set-price { font-size: 38px; font-weight: bold; margin: 0; line-height: 1; }
    .set-change { font-size: 18px; font-weight: bold; margin: 5px 0 0 0; }
    .color-green { color: #00ff44; }
    .color-red { color: #ff3333; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Ultimate Stock Analyzer Pro")
st.markdown("ระบบวิเคราะห์การลงทุน 360 องศา (งบการเงิน + มูลค่า + ปัจจัยเชิงคุณภาพ)")

top_50_companies = {
    "AAPL": "Apple Inc.", "MSFT": "Microsoft", "GOOGL": "Alphabet", 
    "AMZN": "Amazon", "NVDA": "NVIDIA", "META": "Meta Platforms",
    "TSLA": "Tesla", "BRK-B": "Berkshire Hathaway", "LLY": "Eli Lilly", 
    "V": "Visa", "JPM": "JPMorgan Chase", "WMT": "Walmart"
}

st.sidebar.header(" แผงควบคุม")
selected_ticker = st.sidebar.selectbox(
    "เลือกบริษัทที่ต้องการวิเคราะห์:",
    options=list(top_50_companies.keys()),
    format_func=lambda x: f"{x} - {top_50_companies[x]}"
)

if st.sidebar.button(" วิเคราะห์หุ้น "):
    with st.spinner(f"กำลังดึงข้อมูลและแปลภาษาของ {selected_ticker} (อาจใช้เวลาสักครู่)..."):
        ticker = yf.Ticker(selected_ticker)
        
        # ==========================================
        # 1. ดึงข้อมูลราคาแบบใหม่ (แก้ปัญหาโหลดไม่สมบูรณ์)
        # ==========================================
        hist = ticker.history(period="1y")
        
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            pct_change = (change / prev_close) * 100
            
            color_class = "color-green" if change >= 0 else "color-red"
            sign = "+" if change >= 0 else ""
            
            # วาด Banner แถบสีดำเหมือน SET
            st.markdown(f"""
            <div class="set-banner">
                <div>
                    <p class="set-ticker">{selected_ticker}</p>
                    <p class="set-name">{top_50_companies.get(selected_ticker, "")}</p>
                </div>
                <div class="set-price-box">
                    <p class="set-price {color_class}">{current_price:,.2f}</p>
                    <p class="set-change {color_class}">{sign}{change:,.2f} ({sign}{pct_change:,.2f}%)</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ==========================================
            # 2. กราฟราคาหุ้น (โคลนนิ่งสไตล์ SET สีเขียว)
            # ==========================================
            st.markdown("### 📊 กราฟราคาหุ้นย้อนหลัง 1 ปี (Price Chart)")
            fig_price = go.Figure()
            
            # กำหนดสีเส้นกราฟตามราคาบวก/ลบ
            line_color = '#00b050' if change >= 0 else '#ff3333'
            fill_color = 'rgba(0, 176, 80, 0.15)' if change >= 0 else 'rgba(255, 51, 51, 0.15)'

            fig_price.add_trace(go.Scatter(
                x=hist.index, y=hist['Close'],
                mode='lines',
                line=dict(color=line_color, width=2.5),
                fill='tozeroy',
                fillcolor=fill_color,
                name="Price"
            ))
            
            fig_price.update_layout(
                plot_bgcolor='white', paper_bgcolor='white',
                height=350, margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, showline=True, linecolor='#dddddd'),
                yaxis=dict(showgrid=True, gridcolor='#eeeeee', showline=True, linecolor='#dddddd')
            )
            st.plotly_chart(fig_price, use_container_width=True)

        else:
            st.error("ไม่สามารถดึงข้อมูลราคาของบริษัทนี้ได้")

        st.markdown("---")

        # ==========================================
        # 3. จัดการระบบแปลภาษาแบบรัดกุม
        # ==========================================
        try:
            info = ticker.info
        except:
            info = {}

        with st.expander("📖 อ่านรายละเอียดธุรกิจ (Business Summary - แปลไทยอัตโนมัติ)", expanded=True):
            summary_en = info.get('longBusinessSummary', '')
            if summary_en:
                try:
                    translator = GoogleTranslator(source='auto', target='th')
                    # ซอยข้อความเพื่อป้องกัน Error จากการแปลข้อความยาวเกินไป
                    summary_th = translator.translate(summary_en[:2000]) 
                    st.markdown(f"**🇹🇭 ฉบับแปลภาษาไทย:**\n\n{summary_th}")
                    st.markdown("---")
                    st.markdown(f"**🇺🇸 ต้นฉบับ (Original):**\n\n<span style='color:gray'>{summary_en}</span>", unsafe_allow_html=True)
                except Exception as e:
                    st.write(summary_en)
                    st.caption("(⚠️ ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์แปลภาษาได้ชั่วคราว แสดงผลต้นฉบับแทน)")
            else:
                st.info("📌 Yahoo Finance ไม่มีข้อมูลรายละเอียดธุรกิจของบริษัทนี้ในระบบ")

        st.markdown("---")

        # ==========================================
        # 4. เครื่องจับโกหกงบการเงิน (Forensic)
        # ==========================================
        st.subheader(" ตรวจสอบบัญชี (Forensic Analysis)")
        try:
            inc = ticker.financials
            cf = ticker.cashflow
            bal = ticker.balance_sheet
            
            if not inc.empty and not cf.empty and not bal.empty:
                net_income = inc.loc['Net Income'].iloc[::-1] if 'Net Income' in inc.index else None
                revenue = inc.loc['Total Revenue'].iloc[::-1] if 'Total Revenue' in inc.index else None
                
                cfo_candidates = ['Operating Cash Flow', 'Total Cash From Operating Activities']
                cfo_name = next((name for name in cfo_candidates if name in cf.index), None)
                cfo = cf.loc[cfo_name].iloc[::-1] if cfo_name else None
                
                rec_candidates = ['Accounts Receivable', 'Net Receivables']
                rec_name = next((name for name in rec_candidates if name in bal.index), None)
                receivables = bal.loc[rec_name].iloc[::-1] if rec_name else None
                
                inventory = bal.loc['Inventory'].iloc[::-1] if 'Inventory' in bal.index else None
                
                if net_income is not None and cfo is not None:
                    years = [str(year)[:4] for year in net_income.index]
                    
                    # กราฟแท่งกำไร vs เงินสด
                    fig_forensic = go.Figure()
                    fig_forensic.add_trace(go.Bar(x=years, y=net_income.values, name='กำไรสุทธิ (Net Income)', marker_color='#3b82f6'))
                    fig_forensic.add_trace(go.Bar(x=years, y=cfo.values, name='เงินสดดำเนินงาน (CFO)', marker_color='#00b050'))
                    fig_forensic.update_layout(
                        barmode='group', height=350, 
                        title='คุณภาพกำไร: เงินสดของจริง (สีเขียว) ต้องสอดคล้องกับกำไร (สีฟ้า)',
                        plot_bgcolor='white', paper_bgcolor='white',
                        yaxis=dict(showgrid=True, gridcolor='#eeeeee')
                    )
                    st.plotly_chart(fig_forensic, use_container_width=True)
                    
                    # ---------------- Action Plan ----------------
                    st.markdown("### 📋 สรุปผลการวิเคราะห์ และ คำแนะนำ (Action Plan)")
                    flags = 0
                    
                    if net_income.iloc[-1] > 0 and cfo.iloc[-1] <= 0:
                        st.error("🚨 **RED FLAG 1: กำไรสุทธิโต แต่กระแสเงินสดดำเนินงานติดลบ**")
                        st.markdown("""
                        > **💡 ความหมาย:** บริษัทรายงานว่ามีกำไร แต่ในความเป็นจริงเก็บเงินสดจากลูกค้าไม่ได้เลย 
                        > **🎯 สิ่งที่ควรทำ:** หลีกเลี่ยงการลงทุนชั่วคราว จนกว่าจะเจาะลึกงบกระแสเงินสดว่าเงินจมไปกับอะไร หากจมไปกับ 'ลูกหนี้การค้า' จำนวนมาก ถือว่ามีความเสี่ยงสูงในการตกแต่งบัญชี
                        """)
                        flags += 1
                        
                    if receivables is not None and revenue is not None:
                        rev_growth = revenue.pct_change().iloc[-1]
                        rec_growth = receivables.pct_change().iloc[-1]
                        if not np.isnan(rec_growth) and not np.isnan(rev_growth) and rec_growth > (rev_growth * 2) and rec_growth > 0.1:
                            st.error(f"🚨 **RED FLAG 2: ลูกหนี้การค้าโตเร็วกว่ายอดขาย (Aggressive Receivables)**")
                            st.markdown(f"""
                            > **💡 ความหมาย:** ยอดขายเติบโต {rev_growth*100:.1f}% แต่ลูกหนี้กลับโตถึง {rec_growth*100:.1f}% แปลว่าบริษัทอาจใช้วิธียัดไส้ยอดขาย เพื่อให้งบดูดี
                            > **🎯 สิ่งที่ควรทำ:** ตรวจสอบหมายเหตุประกอบงบการเงินเรื่อง 'อายุลูกหนี้การค้า' ว่ามีลูกหนี้ที่ค้างชำระเกิน 90 วันเพิ่มขึ้นผิดปกติหรือไม่
                            """)
                            flags += 1
                            
                    if inventory is not None and revenue is not None:
                        rev_growth = revenue.pct_change().iloc[-1]
                        inv_growth = inventory.pct_change().iloc[-1]
                        if not np.isnan(inv_growth) and not np.isnan(rev_growth) and inv_growth > 0.05 and rev_growth < 0:
                            st.warning("⚠️ **YELLOW FLAG: สินค้าคงคลังล้นสต็อก สวนทางยอดขาย (Inventory Piling Up)**")
                            st.markdown("""
                            > **💡 ความหมาย:** ยอดขายของบริษัทกำลังลดลง แต่สต็อกสินค้าในโกดังกลับบวมขึ้นเรื่อยๆ 
                            > **🎯 สิ่งที่ควรทำ:** หากบริษัทขายสินค้าที่ตกรุ่นง่าย ให้ระวังการขาดทุนจากการด้อยค่าสินค้า แต่ถ้าเป็นธุรกิจสินค้าโภคภัณฑ์ อาจเป็นการกักตุนสินค้ารอราคาขึ้น
                            """)
                            flags += 1
                            
                    if flags == 0:
                        st.success("🟢 **GREEN FLAG: งบการเงินเบื้องต้นแข็งแกร่ง ปลอดภัย**")
                        st.markdown("""
                        > **💡 ความหมาย:** ไม่พบความผิดปกติที่ขัดแย้งกันอย่างมีนัยสำคัญระหว่าง กำไรทางบัญชี กับ กระแสเงินสดจริง
                        > **🎯 สิ่งที่ควรทำ:** สอบผ่านเกณฑ์คุณภาพงบการเงิน สามารถพิจารณาลงทุนตามหลักการประเมินมูลค่า (Valuation) พื้นฐานต่อไปได้
                        """)
                else:
                     st.warning("โครงสร้างบัญชีไม่ครบถ้วน ไม่สามารถประเมิน Forensic ได้")
            else:
                st.error("ไม่มีข้อมูลงบการเงินย้อนหลังเพียงพอ")
        except Exception as e:
            st.error("เกิดข้อผิดพลาดในการดึงข้อมูลบัญชี")
