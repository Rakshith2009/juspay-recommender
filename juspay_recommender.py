import streamlit as st
import pandas as pd

st.set_page_config(page_title="Juspay Payments Journey", layout="wide")

# -------------------------
# Product catalog with must-have and good-to-have by industry + Juspay Features
# -------------------------
PRODUCTS = {
    "UPI": {
        "category": "Payments",
        "features": ["instant", "low-cost", "popular"],
        "why": "UPI is the backbone of Indian digital payments. Merchants love it for low MDR and instant confirmation.",
        "api_calls": ["/session", "/upi/intent", "/status", "/retry"],
        "api_reason": "Collect money instantly → check status → retry if needed.",
        "inter_api_flow": "App → Juspay API → NPCI → Issuer Bank → Acquirer Bank → Confirmation → Merchant.",
        "banks_supported": ["HDFC Bank", "ICICI Bank", "Axis Bank", "SBI"],
        "integration": "1. Create an order → 2. Call /upi/intent → 3. Poll /status → 4. Retry if pending.",
        "regulation": "Must comply with NPCI guidelines on limits, recurring mandates, and fraud monitoring.",
        "must_have": ["e-commerce", "FinTech / InsurTech", "Insurance", "Travel", "Education", "Gaming", "Hyper Local", "Billpay", "BFSI", "Telcomm", "AgriTech", "NBFC", "E-Pharma", "Stock Broking", "Ticketing", "OTT", "Classified", "Food Tech", "Media / Telecom / OT", "Hospitality", "EdTech"],
        "good_to_have": []
    },
    "Cards with Tokenization": {
        "category": "Payments",
        "features": ["cards", "secure", "recurring"],
        "why": "Cards are widely used. RBI mandates tokenization for card-on-file transactions, improving security.",
        "api_calls": ["/session", "/card/tokenize", "/payment", "/status", "/vault"],
        "api_reason": "Convert sensitive card numbers into tokens → use them safely for payments.",
        "inter_api_flow": "Merchant → Juspay /session → Juspay /card/tokenize → Card Network → Issuer Bank → Confirmation.",
        "banks_supported": ["Visa", "Mastercard", "RuPay"],
        "integration": "1. Create token → 2. Save token → 3. Use token for payment → 4. Track status.",
        "regulation": "RBI (2022) mandates tokenization; merchants cannot store raw card numbers.",
        "must_have": ["e-commerce", "Travel", "E-Retail", "Hospitality"],
        "good_to_have": ["EdTech"]
    },
    "Netbanking": {
        "category": "Payments",
        "features": ["bank-direct", "traditional"],
        "why": "Netbanking is still used for high-ticket items and by customers not on UPI/cards.",
        "api_calls": ["/session", "/nb/start", "/status"],
        "api_reason": "Redirect customer → they log in to bank → bank confirms → Juspay updates.",
        "inter_api_flow": "App → Juspay session → Bank login → Bank confirms to Juspay → Merchant notified.",
        "banks_supported": ["ICICI", "Axis", "HDFC", "SBI", "Kotak"],
        "integration": "1. Create order → 2. Redirect via /nb/start → 3. Poll /status.",
        "regulation": "Governed by RBI guidelines; 2FA required.",
        "must_have": ["Travel", "EdTech", "Hospitality", "BFSI"],
        "good_to_have": ["e-commerce"]
    },
}

# -------------------------
# Juspay Feature Add-ons (independent of industry) + Merchants Using
# -------------------------
FEATURE_ADDONS = {
    "Product Summary": {
        "category": "Payment Suite V2",
        "why": "Show users a neat order summary during checkout.",
        "api_calls": ["/session/summary"],
        "integration": "Use summary API to display cart/order details.",
        "demo_video": "https://juspay.io/in/docs/product-summary/docs/product-summary/overview",
        "merchants_using": []
    },
    "Payment Locking": {
        "category": "Payment Suite V2",
        "why": "Block or allow payment methods based on rules.",
        "api_calls": ["/payment_lock"],
        "integration": "Define lock rules → Call API before showing payment screen.",
        "demo_video": "https://juspay.io/in/docs/payment-locking/docs/payment-locking/overview",
        "merchants_using": []
    },
    "Quick Pay": {
        "category": "Payment Suite V2",
        "why": "Enable 1-click checkout from cart page.",
        "api_calls": ["/quickpay/initiate", "/quickpay/confirm"],
        "integration": "Save preferred payment → Call QuickPay API → Auto-confirm order.",
        "demo_video": "https://juspay.io/in/docs/quickpay-integration/docs/quick-pay/overview",
        "merchants_using": []
    },
    "Retry": {
        "category": "Payment Suite V2",
        "why": "Let users quickly retry failed transactions.",
        "api_calls": ["/retry/initiate", "/retry/status"],
        "integration": "Capture failure → Trigger retry API → Show result.",
        "demo_video": "https://juspay.io/in/docs/retry/docs/retry/overview",
        "merchants_using": []
    },
    "UPI Autopay": {
        "category": "Payment Suite V2",
        "why": "Enable auto-debit for subscriptions via UPI.",
        "api_calls": ["/upi/mandate/create", "/upi/mandate/execute", "/upi/mandate/status"],
        "integration": "User approves mandate → NPCI registers → Auto debit via execute API.",
        "demo_video": "https://juspay.io/in/docs/upi-autopay/docs/upi-autopay/overview",
        "merchants_using": ["Gaana (subscriptions)", "Netflix", "Hotstar", "Angel Broking", "5Paisa"]
    },
    "Outages": {
        "category": "Payment Suite V2",
        "why": "Smart rerouting with real-time payment health updates.",
        "api_calls": ["/system/health"],
        "integration": "Integrate health API → auto-switch flows during outages.",
        "demo_video": "https://juspay.io/in/docs/outages/docs/outages/overview",
        "merchants_using": []
    },
    "UPI Intent on mWeb": {
        "category": "Payment Suite V2",
        "why": "Enable UPI on mobile web with app redirect.",
        "api_calls": ["/upi/intent/mweb"],
        "integration": "Trigger intent → Redirect user to UPI app.",
        "demo_video": "https://juspay.io/in/docs/mweb-intent/docs/upi-intent-on-mweb/overview",
        "merchants_using": []
    },
    "HyperUPI (In-app UPI SDK)": {
        "category": "Payment Suite V2",
        "why": "Enable seamless UPI experience inside apps via NPCI's Plug-in SDK.",
        "api_calls": ["/hyperupi/initiate", "/hyperupi/confirm"],
        "integration": "Integrate HyperUPI SDK → Enable one-click UPI inside your app.",
        "demo_video": "https://juspay.io/in/docs/hyperupi/docs/hyperupi/overview",
        "merchants_using": ["Gullak"]
    }
}

# -------------------------
# Recommendation function
# -------------------------
def recommend(industry):
    recs = []
    for name, details in PRODUCTS.items():
        if industry in details.get("must_have", []) or industry in details.get("good_to_have", []):
            recs.append({
                "Product": name,
                "Category": details.get("category", "General"),
                "Why it matters": details.get("why", ""),
                "API Calls": details.get("api_calls", []),
                "Layman API Reason": details.get("api_reason", ""),
                "Inter-API Communication": details.get("inter_api_flow", "Not available"),
                "Banks Supported": details.get("banks_supported", []),
                "Integration Steps": details.get("integration", "Details not available"),
                "Regulation": details.get("regulation", "No regulatory notes"),
                "Priority": "Must Have" if industry in details.get("must_have", []) else "Good to Have",
                "Demo Video": "",
                "Merchants Using This": []
            })
    for name, details in FEATURE_ADDONS.items():
        priority = "✨ Recommended Add-on" if name in ["Quick Pay", "Retry", "UPI Autopay"] else "Add-on"
        recs.append({
            "Product": name,
            "Category": details.get("category", "Add-on"),
            "Why it matters": details.get("why", ""),
            "API Calls": details.get("api_calls", []),
            "Layman API Reason": "",
            "Inter-API Communication": "Not applicable",
            "Banks Supported": [],
            "Integration Steps": details.get("integration", "Plug-and-play feature"),
            "Regulation": "No regulatory notes",
            "Priority": priority,
            "Demo Video": details.get("demo_video", ""),
            "Merchants Using This": details.get("merchants_using", [])
        })
    return pd.DataFrame(recs)

# -------------------------
# Streamlit UI
# -------------------------
st.title("🚀 Juspay Payments Journey")
st.write("Easily explore Juspay products and features tailored to your business.")

industry = st.selectbox("💼 Select your business category:", 
    sorted(["e-commerce", "Hyper Local", "Billpay", "Travel", "BFSI", "E-Retail", "Telcomm", "AgriTech", "NBFC", "E-Pharma", "Stock Broking", "Insurance", "Ticketing", "OTT", "Hyperlocal", "Classified", "FinTech / InsurTech", "Food Tech", "Other", "Media / Telecom / OT", "Hospitality", "EdTech"]))

if st.button("✨ Show My Journey"):
    df = recommend(industry)
    if df.empty:
        st.error("No matching Juspay products found for your selection.")
    else:
        for i, r in df.iterrows():
            with st.expander(f"📦 {r['Product']} ({r['Priority']})", expanded=(r['Priority'] == "Must Have" or r['Priority'] == "✨ Recommended Add-on")):
                st.markdown(f"**📂 Category:** {r['Category']}")
                st.markdown(f"**💡 Why it matters:** {r['Why it matters']}")
                if r['API Calls']:
                    st.markdown(f"**🔌 API Calls involved:** {', '.join(r['API Calls'])}")
                if r['Layman API Reason']:
                    st.markdown(f"**🗣 In simple words:** {r['Layman API Reason']}")
                if r['Inter-API Communication']:
                    st.markdown(f"**🔄 Inter-API Communication:** {r['Inter-API Communication']}")
                if r['Banks Supported']:
                    st.markdown(f"**🏦 Supported Banks/Networks:** {', '.join(r['Banks Supported'])}")
                if r['Integration Steps']:
                    st.markdown(f"**⚙️ Integration Steps:** {r['Integration Steps']}")
                if r['Regulation']:
                    st.markdown(f"**📜 Regulatory note (RBI):** {r['Regulation']}")
                if r['Demo Video']:
                    st.markdown(f"**🎥 Demo Video:** [Watch here]({r['Demo Video']})")
                if r['Merchants Using This']:
                    st.markdown(f"**🤝 Who’s already using this:** {', '.join(r['Merchants Using This'])}")
