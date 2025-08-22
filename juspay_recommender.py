
# =========================
# juspay_recommender.py
# =========================
import streamlit as st
import pandas as pd
from typing import Dict, List

st.set_page_config(page_title="Juspay Product Recommender", page_icon="💳", layout="wide")

# ---------- UI HEADER ----------
st.title("💳 Juspay Product Recommender")
st.caption("Tell us about your business — we’ll suggest the right Juspay products in simple language, plus handy add‑ons.")

# ---------- BASE PRODUCTS (Platforms) ----------
PRODUCTS: Dict[str, Dict] = {
    "UPI": {
        "why": "Instant bank‑to‑bank payments, huge adoption, 24/7 — boosts success and customer preference.",
        "integration": "Use Express Checkout to start a UPI payment (Intent/Collect) and poll for status.",
        "apis": ["initiatePayment", "checkPaymentStatus", "retryPayment (optional)"],
        "api_reason": "Ask for money → check if paid → try again if needed. Like ringing the bell, then opening the door.",
        "features": "UPI Intent & Collect, deep link, PSP coverage, auto‑retries, success optimization.",
        "docs": "https://juspay.io/in/docs/api-reference/docs/express-checkout/introduction",
    },
    "Cards with Tokenization": {
        "why": "Save cards safely for one‑click checkout (RBI compliant). Lifts conversion and reduces friction.",
        "integration": "Integrate Juspay Safe to tokenise and charge tokens.",
        "apis": ["tokenizeCard", "chargeTokenizedCard", "deleteCardToken"],
        "api_reason": "Give the card a safe nickname (token) and charge the nickname — real number stays hidden.",
        "features": "Visa/Mastercard/RuPay tokens, one‑click pay, better approvals.",
        "docs": "https://juspay.io/in/docs/resources/docs/card-network-tokenization/tokenization--express-checkout-card-vault-merchants",
    },
    "Subscriptions": {
        "why": "Automates repeat billing for SaaS/OTT/insurance — predictable revenue, less manual work.",
        "integration": "Create/manage mandates; charge on schedule (UPI Autopay, eNACH, Cards).",
        "apis": ["createMandate", "debitMandate", "cancelMandate", "getMandateStatus"],
        "api_reason": "Set the rule → run the charge → cancel/track when needed. Like a standing order.",
        "features": "UPI Autopay, eNACH, card mandates, reminders/pre‑debit alerts.",
        "docs": "https://juspay.io/in/docs/api-reference/docs/express-checkout/introduction",
    },
    "Refunds": {
        "why": "Fast refunds build trust and reduce support tickets.",
        "integration": "Trigger refund API when order is cancelled/returned; track status.",
        "apis": ["refundOrder", "checkRefundStatus"],
        "api_reason": "Send money back and verify it reached the customer.",
        "features": "Full/partial refunds, notifications, status tracking.",
        "docs": "https://juspay.io/in/docs/api-reference/docs/express-checkout/refund-order-api",
    },
    "Payment Orchestration": {
        "why": "Auto‑route via the best acquirer/PSP to reduce failures and lift approval rates.",
        "integration": "Configure rules and fallbacks in the orchestration layer.",
        "apis": ["routeTransaction", "retryTransaction", "getRouteMetrics"],
        "api_reason": "Pick the fastest checkout lane; switch and retry if a lane is slow.",
        "features": "Multi‑gateway routing, smart retries, data‑driven rules.",
        "docs": "https://juspay.io/in/docs/api-reference/docs/express-checkout/introduction",
    },
    "Offers & Discounts": {
        "why": "Delight customers and drive conversion with coupons, bank offers, EMI offers.",
        "integration": "Configure offers in dashboard; validate/apply at checkout.",
        "apis": ["applyOffer", "validateOffer"],
        "api_reason": "Like scanning a coupon at the counter — apply only when eligible.",
        "features": "Promo codes, issuer offers, instant discounts/cashback.",
        "docs": "https://juspay.io/in/docs/api-reference/docs/express-checkout/introduction",
    },
    "Payouts": {
        "why": "Send money to vendors/partners/customers instantly — great for marketplaces and credits.",
        "integration": "Create payout → track status → reconcile.",
        "apis": ["createPayout", "checkPayoutStatus", "listPayouts"],
        "api_reason": "Schedule a transfer and track delivery — like a reliable courier.",
        "features": "Bulk payouts, UPI/IMPS/NEFT, near‑instant settlements.",
        "docs": "https://juspay.io/in/docs/api-reference/docs/express-checkout/introduction",
    },
}

# ---------- FEATURE ADD‑ONS (from your reference list) ----------
FEATURE_ADDONS: Dict[str, Dict] = {
    "Quick Pay": {
        "why": "Lightning‑fast repeat payments with pre‑filled details — fewer taps, higher conversion.",
        "when": "Best for returning users in e‑commerce, ticketing, food tech.",
        "apis": ["initiatePayment (prefilled)", "authorizePayment"],
        "api_reason": "Skip re‑entering info; jump straight to pay securely.",
        "docs": "https://juspay.io/in/docs/quickpay-integration/docs/quick-pay/overview",
        "demo": "(see docs)",
    },
    "Retry": {
        "why": "Auto‑recover failed payments by retrying intelligent paths — boosts success rates.",
        "when": "High traffic or high failure scenarios; anytime approval rate matters.",
        "apis": ["retryPayment", "getRetryOptions"],
        "api_reason": "If one path fails, try a better one automatically.",
        "docs": "https://juspay.io/in/docs/retry/docs/retry/overview",
        "demo": "(see docs)",
    },
    "UPI Autopay": {
        "why": "Set‑and‑forget recurring UPI payments with customer mandates.",
        "when": "SaaS, insurance premia, subscriptions, savings plans.",
        "apis": ["createMandate", "debitMandate", "cancelMandate"],
        "api_reason": "Create the rule once; charges happen on schedule with alerts.",
        "docs": "https://juspay.io/in/docs/upi-autopay/docs/upi-autopay/overview",
        "demo": "(see docs)",
    },
    "Payment Locking": {
        "why": "Prevent duplicate charges or double‑click payments in high‑traffic checkouts.",
        "when": "Flash sales, ticketing drops, high concurrency.",
        "apis": ["lockPayment", "releaseLock"],
        "api_reason": "Reserve a spot for a payment so it isn’t created twice.",
        "docs": "https://juspay.io/in/docs/payment-locking/docs/payment-locking/overview",
        "demo": "(see docs)",
    },
    "Outages": {
        "why": "Gracefully handle bank/PSP downtime with live signals and routing.",
        "when": "Always‑on; mission‑critical checkout.",
        "apis": ["getOutageStatus", "pauseRoute", "resumeRoute"],
        "api_reason": "If a road is closed, take a detour automatically.",
        "docs": "https://juspay.io/in/docs/outages/docs/outages/overview",
        "demo": "(see docs)",
    },
    "UPI Intent on mWeb": {
        "why": "Open UPI apps from mobile web for higher success vs. QR/Collect only.",
        "when": "Merchants with mobile web flows.",
        "apis": ["initiatePayment (intent)", "checkPaymentStatus"],
        "api_reason": "Tap a button → jump to UPI app → return with status.",
        "docs": "https://juspay.io/in/docs/mweb-intent/docs/upi-intent-on-mweb/overview",
        "demo": "(see docs)",
    },
    "Scan & Pay": {
        "why": "Let customers pay by scanning a dynamic/static UPI QR.",
        "when": "In‑store, COD, deliveries, kiosks.",
        "apis": ["createQR", "checkPaymentStatus", "closeQR"],
        "api_reason": "Show a code → customer scans → confirm payment received.",
        "docs": "https://juspay.io/in/docs/upi-qr-code/docs/scan--pay/overview",
        "demo": "(see docs)",
    },
    "Card Mandates": {
        "why": "Recurring card payments using RBI‑compliant mandates.",
        "when": "Subscriptions where cards are preferred.",
        "apis": ["setupCardMandate", "chargeMandate", "cancelMandate"],
        "api_reason": "Create a permission once, then charge within allowed rules.",
        "docs": "http://juspay.io/in/docs/card-mandates/docs/card-mandate/overview",
        "demo": "(see docs)",
    },
    "eNACH": {
        "why": "Bank account mandates for recurring debits — great for NBFCs/insurers.",
        "when": "Loans, SIPs, insurance premia.",
        "apis": ["createENachMandate", "debitENach", "cancelENach"],
        "api_reason": "Customer authorises bank; collections run automatically.",
        "docs": "https://juspay.io/in/docs/enach/docs/enach/overview",
        "demo": "(see docs)",
    },
    "TPV": {
        "why": "Third‑Party Validation for bank‑mapped payments — reduce wrong credits.",
        "when": "Billpay, utilities, wallets.",
        "apis": ["validateAccount", "linkTPVReference"],
        "api_reason": "Check the account before accepting money.",
        "docs": "https://juspay.io/in/docs/tpv/docs/third-party-validation/overview",
        "demo": "(see docs)",
    },
    "Simpl Paylater": {
        "why": "Offer Buy‑Now‑Pay‑Later via Simpl — lift AOV and conversion.",
        "when": "E‑commerce, D2C, ticketing.",
        "apis": ["startBNPL", "captureBNPL"],
        "api_reason": "Let customers pay later while you get paid now.",
        "docs": "https://juspay.io/in/docs/simpl/docs/simpl-paylater/overview",
        "demo": "(see docs)",
    },
    "Simpl Pay‑in‑3": {
        "why": "Split bills into 3 payments — friendly instalments.",
        "when": "High‑value carts.",
        "apis": ["startBNPL", "captureBNPL"],
        "api_reason": "Break the payment into smaller bites.",
        "docs": "https://juspay.io/in/docs/simpl-pay-in-3/docs/simpl-payin3/overview",
        "demo": "(see docs)",
    },
    "Amazon Pay Balance": {
        "why": "Wallet option with strong customer trust.",
        "when": "Wider choice at checkout.",
        "apis": ["initiateWalletPay", "verifyWalletPay"],
        "api_reason": "Pay using stored wallet balance.",
        "docs": "https://juspay.io/in/docs/amazonpay/docs/amazon-pay-balance/overview",
        "demo": "(see docs)",
    },
    "Juspay Native OTP": {
        "why": "Faster OTP auto‑read and autofill in app — fewer drop‑offs.",
        "when": "Android/iOS apps using cards/EMI.",
        "apis": ["initiateOtp", "verifyOtp"],
        "api_reason": "Read/submit OTP smoothly without friction.",
        "docs": "https://juspay.io/in/docs/dotp-v2/docs/native-otp/overview",
        "demo": "(see docs)",
    },
    "CVV Less Payments": {
        "why": "Reduce steps by skipping CVV on eligible tokenised cards.",
        "when": "Returning users with tokens.",
        "apis": ["chargeTokenizedCard (cvvless)", "riskCheck"],
        "api_reason": "Use safe tokens and risk rules to skip typing CVV.",
        "docs": "https://juspay.io/in/docs/cvv-less/docs/cvv-less-payments/overview",
        "demo": "(see docs)",
    },
    "Tap & Pay": {
        "why": "Contactless in‑person card payments via NFC — very fast.",
        "when": "In‑store, delivery, events.",
        "apis": ["initiateNFC", "captureNFC"],
        "api_reason": "Tap the card/phone and capture the payment.",
        "docs": "https://juspay.io/in/docs/nfc/docs/tap--pay/overview",
        "demo": "(see docs)",
    },
    "O2P with Passkeys": {
        "why": "One‑to‑Pay (Click to Pay) with passkeys for passwordless auth.",
        "when": "Card heavy merchants wanting fast SCA.",
        "apis": ["createPasskey", "authenticatePasskey"],
        "api_reason": "Use device credentials instead of passwords.",
        "docs": "https://juspay.io/in/docs/clicktopay/docs/clicktopay-with-passkeys/overview",
        "demo": "(see docs)",
    },
    "Offers Engine": {
        "why": "Run granular promos (banks, cards, SKUs) without dev churn.",
        "when": "Seasonal sales, issuer tie‑ups.",
        "apis": ["applyOffer", "validateOffer"],
        "api_reason": "Check eligibility and apply savings in real time.",
        "docs": "https://juspay.io/in/docs/offer-engine/docs/offer-engine/overview",
        "demo": "(see docs)",
    },
    "Standard EMI Suite": {
        "why": "Let customers split via issuer EMIs — boosts affordability.",
        "when": "High‑value carts across categories.",
        "apis": ["showEmiOptions", "convertToEmi"],
        "api_reason": "Expose EMI options, convert the charge into instalments.",
        "docs": "https://juspay.io/in/docs/emi/docs/standard-emi-suite/overview",
        "demo": "(see docs)",
    },
    "Advance EMI Suite": {
        "why": "Advanced issuer & cardless EMI flows.",
        "when": "Broader EMI coverage and promos.",
        "apis": ["showEmiOptions", "convertToEmi"],
        "api_reason": "Offer richer EMI plans during checkout.",
        "docs": "https://juspay.io/in/docs/advance-emi/docs/advance-emi-suite/overview",
        "demo": "(see docs)",
    },
    "Payment Links": {
        "why": "Collect payments without a website/app — share a link.",
        "when": "Inside chats, emails, invoices.",
        "apis": ["createPaymentLink", "cancelPaymentLink"],
        "api_reason": "Generate a pay page and track completion.",
        "docs": "https://juspay.io/in/docs/payment-links/docs/payment-links/overview",
        "demo": "(see docs)",
    },
    "Split Settlements": {
        "why": "Split a single payment to multiple parties — great for marketplaces.",
        "when": "Multi‑seller platforms, commissions, affiliates.",
        "apis": ["createSplit", "settleSplit", "reverseSplit"],
        "api_reason": "Route shares to the right parties automatically.",
        "docs": "https://juspay.io/in/docs/split-settlements/docs/split-settlements/overview",
        "demo": "(see docs)",
    },
    "Merchant’s In‑house Wallet": {
        "why": "Offer your own stored‑value wallet for faster repeat purchases.",
        "when": "Loyalty ecosystems, refunds, micro‑purchases.",
        "apis": ["createWallet", "creditWallet", "debitWallet"],
        "api_reason": "Top‑up and spend within your brand’s wallet.",
        "docs": "https://juspay.io/in/docs/merchant-container/docs/merchants-inhouse-wallet/overview",
        "demo": "(see docs)",
    },
    "Part Payment": {
        "why": "Allow customers to pay a portion now and the rest later.",
        "when": "Pre‑orders, bookings, deposits.",
        "apis": ["createPartPayment", "collectBalance"],
        "api_reason": "Take a token amount first, then the remainder.",
        "docs": "https://juspay.io/in/docs/part-payments/docs/overview/description",
        "demo": "(see docs)",
    },
}

# ---------- INDUSTRIES ----------
BUSINESS_CATEGORIES = [
    "e-commerce", "Hyper Local", "Billpay", "Travel", "BFSI", "E-Retail", "Telcomm", "AgriTech", "NBFC",
    "E-Pharma", "Stock Broking", "Insurance", "Ticketing", "OTT", "Hyperlocal", "Classified",
    "FinTech / InsurTech", "Food Tech", "Other", "Media / Telecom / OT", "Hospitality", "EdTech"
]

# Defaults per industry (editable): what’s must‑have vs good‑to‑have
INDUSTRY_DEFAULTS: Dict[str, Dict[str, List[str]]] = {
    "e-commerce": {
        "must": ["UPI", "Cards with Tokenization", "Refunds"],
        "good": ["Payment Orchestration", "Offers & Discounts", "Quick Pay", "Retry", "UPI Intent on mWeb"]
    },
    "BFSI": {
        "must": ["UPI", "Payment Links", "TPV"],
        "good": ["Subscriptions", "eNACH", "Split Settlements", "UPI Autopay"]
    },
    "Travel": {
        "must": ["UPI", "Cards with Tokenization", "Refunds"],
        "good": ["Split Settlements", "Quick Pay", "Retry", "Offers & Discounts"]
    },
    "NBFC": {
        "must": ["eNACH", "UPI Autopay", "TPV"],
        "good": ["Payment Links", "Part Payment", "Merchant’s In‑house Wallet"]
    },
    "Insurance": {
        "must": ["UPI Autopay", "eNACH", "Subscriptions"],
        "good": ["Payment Links", "TPV", "Offers Engine"]
    },
}

# ---------- HELPER: build recommendation ----------
def build_recommendation(industry: str, channel: str, scale: str, needs: Dict[str, bool]) -> Dict[str, List[Dict]]:
    must, good = [], []

    # Start with industry defaults
    defaults = INDUSTRY_DEFAULTS.get(industry, {"must": ["UPI"], "good": ["Payment Orchestration"]})
    for p in defaults["must"]:
        source = PRODUCTS.get(p) or FEATURE_ADDONS.get(p)
        if source:
            must.append({"name": p, **source})
    for p in defaults["good"]:
        source = PRODUCTS.get(p) or FEATURE_ADDONS.get(p)
        if source:
            good.append({"name": p, **source})

    # Refine by needs
    if needs.get("recurring"):
        for p in ["Subscriptions", "UPI Autopay", "eNACH", "Card Mandates"]:
            source = PRODUCTS.get(p) or FEATURE_ADDONS.get(p)
            if source and not any(x["name"] == p for x in must + good):
                must.append({"name": p, **source})
    if needs.get("emi_bnpl"):
        for p in ["Standard EMI Suite", "Advance EMI Suite", "Simpl Paylater", "Simpl Pay‑in‑3"]:
            source = FEATURE_ADDONS.get(p)
            if source and not any(x["name"] == p for x in must + good):
                good.append({"name": p, **source})
    if needs.get("payouts"):
        p = "Payouts"
        if not any(x["name"] == p for x in must + good):
            must.append({"name": p, **PRODUCTS[p]})
    if needs.get("offers"):
        p = "Offers & Discounts"
        if not any(x["name"] == p for x in must + good):
            good.append({"name": p, **PRODUCTS[p]})
    if needs.get("orchestration") or scale in ["High", "Very High"]:
        for p in ["Payment Orchestration", "Retry"]:
            source = PRODUCTS.get(p) or FEATURE_ADDONS.get(p)
            if source and not any(x["name"] == p for x in must + good):
                good.append({"name": p, **source})

    # Channel hints
    if "App" in channel:
        for p in ["Juspay Native OTP"]:
            source = FEATURE_ADDONS.get(p)
            if source and not any(x["name"] == p for x in must + good):
                good.append({"name": p, **source})
    if "Web" in channel or "App" in channel:
        # Mobile web support
        p = "UPI Intent on mWeb"
        if not any(x["name"] == p for x in must + good):
            good.append({"name": p, **FEATURE_ADDONS[p]})

    # Return as dataframes for display/download
    return {
        "must": must,
        "good": good,
        "df_must": pd.DataFrame([{k: v for k, v in x.items() if k not in ["docs", "demo"]} for x in must]),
        "df_good": pd.DataFrame([{k: v for k, v in x.items() if k not in ["docs", "demo"]} for x in good]),
    }

# ---------- INPUT FORM ----------
st.subheader("1) Tell us about your business")
col1, col2, col3 = st.columns([1,1,1])
with col1:
    industry = st.selectbox("Industry", BUSINESS_CATEGORIES, index=0)
with col2:
    channel = st.radio("Sales Channel", ["App", "Web", "Both"], horizontal=True)
with col3:
    scale = st.select_slider(
        "Transaction Scale",
        options=["Low", "Mid", "High", "Very High"],
        value="Mid",
        help="Rough monthly volume (Low <50k, Mid 200k–500k, High 1M–5M, Very High 10M+)",
    )

st.subheader("2) Optional needs (we auto‑pick a base set per industry)")
colA, colB, colC, colD, colE = st.columns(5)
with colA:
    need_recurring = st.checkbox("Recurring billing")
with colB:
    need_emi = st.checkbox("EMI / BNPL")
with colC:
    need_payouts = st.checkbox("Payouts")
with colD:
    need_offers = st.checkbox("Offers / cashback")
with colE:
    need_orch = st.checkbox("Orchestration")

notes = st.text_input("Any special notes? (optional)")

if st.button("✨ Show my recommendations"):
    needs = {
        "recurring": need_recurring,
        "emi_bnpl": need_emi,
        "payouts": need_payouts,
        "offers": need_offers,
        "orchestration": need_orch,
        "notes": notes or "",
    }

    rec = build_recommendation(industry, channel, scale, needs)

    if rec["df_must"].empty and rec["df_good"].empty:
        st.warning("No clear match yet — try toggling a need like Recurring or EMI.")
    else:
        st.success("Here’s a simple, ready‑to‑share plan.")

        st.markdown("### ✅ Must‑have (start here)")
        if not rec["df_must"].empty:
            for item in rec["must"]:
                with st.expander(f"{item['name']} — {item['why']}"):
                    st.markdown(f"**Why this matters:** {item['why']}")
                    st.markdown(f"**How it works:** {item['integration'] if 'integration' in item else item.get('when','')} ")
                    st.markdown(f"**Key APIs:** {', '.join(item['apis'])}")
                    st.markdown(f"**In plain words:** {item['api_reason']}")
                    st.markdown(f"**Features:** {item.get('features','—')}")
                    if 'docs' in item: st.markdown(f"[Docs]({item['docs']})")
                    if 'demo' in item and item['demo'] != "": st.caption(f"Demo: {item['demo']}")
        else:
            st.write("(No must‑haves — see Good‑to‑have below.)")

        st.markdown("### 👍 Good‑to‑have (add as you scale)")
        if not rec["df_good"].empty:
            for item in rec["good"]:
                with st.expander(f"{item['name']} — {item['why']}"):
                    st.markdown(f"**Why this matters:** {item['why']}")
                    st.markdown(f"**How it works:** {item.get('integration', item.get('when',''))}")
                    st.markdown(f"**Key APIs:** {', '.join(item['apis'])}")
                    st.markdown(f"**In plain words:** {item['api_reason']}")
                    st.markdown(f"**Features:** {item.get('features','—')}")
                    if 'docs' in item: st.markdown(f"[Docs]({item['docs']})")
                    if 'demo' in item and item['demo'] != "": st.caption(f"Demo: {item['demo']}")
        else:
            st.write("(No good‑to‑haves for now.)")

        # Download as CSV (merged)
        df_out = pd.concat([rec["df_must"].assign(Tier="Must‑have"), rec["df_good"].assign(Tier="Good‑to‑have")], ignore_index=True)
        st.download_button(
            label="⬇️ Download my plan (CSV)",
            data=df_out.to_csv(index=False).encode("utf-8"),
            file_name="juspay_recommendations.csv",
            mime="text/csv",
        )

st.divider()
st.markdown("#### ℹ️ Juspay Products — Explained Simply")
with st.expander("See product & add‑on catalog"):
    st.write("Browse the full list with friendly API explanations and docs links.")
    for name, d in {**PRODUCTS, **FEATURE_ADDONS}.items():
        with st.expander(name):
            st.markdown(f"**Why:** {d['why']}")
            st.markdown(f"**Key APIs:** {', '.join(d['apis'])}")
            st.markdown(f"**In plain words:** {d['api_reason']}")
            extra = []
            if d.get('features'): extra.append(f"Features: {d['features']}")
            if d.get('when'): extra.append(f"When to use: {d['when']}")
            if extra: st.markdown(" • ".join(extra))
            if d.get('docs'): st.markdown(f"[Docs]({d['docs']})")
            if d.get('demo'): st.caption(f"Demo: {d['demo']}")
```

---

### requirements.txt
```
streamlit>=1.36
pandas>=1.5
```

### setup.sh (optional, Streamlit Cloud)
```
mkdir -p ~/.streamlit/
cat << 'EOF' > ~/.streamlit/config.toml
[server]
headless = true
port = $PORT
enableCORS = false
EOF
```

### Procfile (optional, Heroku)
```
web: streamlit run juspay_recommender.py --server.port=$PORT --server.address=0.0.0.0
```

### README.md
```
# Juspay Product Recommender

Pick your industry, channel, and scale — get **must‑have** and **good‑to‑have** Juspay products and Feature Add‑ons with friendly API notes and docs links.

## Run locally
```bash
git clone https://github.com/<you>/juspay-recommender
cd juspay-recommender
pip install -r requirements.txt
streamlit run juspay_recommender.py
```

## Deploy
- **Streamlit Cloud**: push this repo → New app → pick `juspay_recommender.py`.
- **Render/Heroku**: use the `Procfile`.
```
