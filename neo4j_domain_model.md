# AstroKiran Neo4j Domain Model

Based on analysis of real data (last 7 days + reference data).

---

## Data Summary (Last 7 Days)

| Category | Table | Records |
|----------|-------|---------|
| **Auth** | auth_users | 3,246 |
| | auth_user_roles | 3,000 |
| | user_sessions | 3,274 |
| | user_devices | 3,039 |
| | login_activities | 7,036 |
| | otp_attempts | 3,762 |
| **Customers** | customer | 2,989 |
| | customer_profile | 3,442 |
| **Guides** | guide_profile | 35 (all) |
| | skills | 10 (ref) |
| | languages | 5 (ref) |
| | guide_skills | 71 (all) |
| | guide_languages | 63 (all) |
| | bank_account | 34 (all) |
| | verification | 170 (all) |
| **Consultations** | consultation | 864 |
| | feedback | 131 |
| | agora_session | 749 |
| | quality_metrics | 514 |
| **Wallet** | user_wallets | 2,989 |
| | consultant_wallets | 34 (all) |
| | payment_orders | 1,393 |
| | wallet_orders | 749 |
| | wallet_transactions | 1,509 |
| | invoices | 668 |
| **Offers** | offer_definitions | 12 (all) |
| | offer_reservations | 689 |
| | offer_consumptions | 1,081 |
| | user_behavior_metrics | 439 |
| | milestone_progress | 629 |
| **Marketing** | leads | 42 |
| **Notifications** | notifications | 15,559 |

---

## Key ID Relationships (from real data)

```
Customer.customer_id (int) ─────┬──── = ───── UserWallet.user_id (int)
                                │
                                └──── x_auth_id ──── AuthUser.id (int)

Guide.id (int) ─────────────────┬──── = ───── ConsultantWallet.consultant_id (int)
                                │
                                └──── x_auth_id ──── AuthUser.id (int)

Consultation ───────────────────┬──── customer_id ──── Customer
                                ├──── guide_id ──────── Guide
                                └──── order_id ──────── WalletOrder

WalletOrder ────────────────────┬──── user_id ──────── UserWallet (= Customer)
                                └──── consultant_id ── Guide

PaymentOrder ───────────────────┬──── user_id ──────── UserWallet (= Customer)
                                └──── gateway_id ───── PaymentGateway

Session/Device ─────────────────┬──── auth_user_id ── AuthUser
                                └──── device_id ────── (shared key)

Notification ───────────────────┬──── auth_user_id ── AuthUser (as string)
                                └──── target_type ─── 'customer' | 'guide'

OfferReservation ───────────────┬──── user_id ──────── Customer
                                ├──── offer_id ─────── Offer
                                └──── consultation_id ─ Consultation (optional)

OfferConsumption ───────────────┬──── user_id ──────── Customer
                                ├──── offer_id ─────── Offer
                                ├──── reservation_id ── OfferReservation (optional)
                                └──── payment_order_id ─ PaymentOrder (optional)
```

---

## Nodes

### Core Identity

| Node | Source | Key Properties | ID Field |
|------|--------|----------------|----------|
| `:AuthUser` | auth.auth_users | phone_number, is_active, is_test_user | id (bigint) |
| `:Customer` | customers.customer | phone_number, country_code | customer_id (bigint) |
| `:Guide` | guide.guide_profile | full_name, phone_number, availability_state, chat/voice/video_enabled, ranking_score, tier | id (bigint) |

### Customer Domain

| Node | Source | Key Properties |
|------|--------|----------------|
| `:CustomerProfile` | customers.customer_profile | name, dob, tob, birth_city, zodiac_sign, gender |
| `:CustomerWallet` | wallet.user_wallets | real_cash, virtual_cash, recharge_count |

### Guide Domain

| Node | Source | Key Properties |
|------|--------|----------------|
| `:Skill` | guide.skills | name, description |
| `:Language` | guide.languages | name |
| `:BankAccount` | guide.bank_account | account_holder_name, bank_name, ifsc_code |
| `:Verification` | guide.verification | target_type, status, verified_at |
| `:SavedMessage` | guide.saved_messages | title, content |
| `:GuideWallet` | wallet.consultant_wallets | revenue_share, accepts_promotional_offers |

### Consultation Domain

| Node | Source | Key Properties |
|------|--------|----------------|
| `:Consultation` | consultation.consultation | mode, state, duration, base_rate_per_minute, is_quick_connect, promotional |
| `:AgoraSession` | consultation.agora_consultation_session | agora_channel_name, duration_seconds, status |
| `:Feedback` | consultation.feedback | rating (1-5), feedback_text, status |
| `:QualityMetrics` | consultation.consultation_quality_metrics | is_short_consultation, message_counts, avg_response_time |

### Financial Domain

| Node | Source | Key Properties |
|------|--------|----------------|
| `:Payment` | wallet.payment_orders | amount, status, payment_method |
| `:WalletOrder` | wallet.wallet_orders | service_type, minutes_ordered, final_amount, consultant_share, status |
| `:Transaction` | wallet.wallet_transactions | type (ADD/SPENT), amount, real_cash_delta, virtual_cash_delta, is_promotional |
| `:Invoice` | wallet.invoices | invoice_number, total_amount |
| `:PaymentGateway` | wallet.payment_gateways | name |
| `:PromotionRule` | wallet.promotion_rules | name, min/max_recharge_amount, virtual_cash_percentage |

### Offers Domain

| Node | Source | Key Properties |
|------|--------|----------------|
| `:Offer` | offers.offer_definitions | offer_name, offer_type, bonus_percentage, free_minutes |
| `:OfferReservation` | offers.offer_reservations | reservation_status, bonus_amount |
| `:OfferConsumption` | offers.offer_consumptions | consumption_status, bonus_amount |
| `:UserBehavior` | offers.user_behavior_metrics | user_type, total_consultations, total_spent, user_segment |
| `:MilestoneProgress` | offers.user_milestone_progress | milestone_reached, trigger_event |

### Auth Domain

| Node | Source | Key Properties |
|------|--------|----------------|
| `:Session` | auth.user_sessions | user_type, is_active, access_token_exp |
| `:Device` | auth.user_devices | device_type, platform, fcm_token |
| `:LoginActivity` | auth.login_activities | action, success, ip_address |
| `:OTPAttempt` | auth.otp_attempts | purpose, is_used, validation_attempts |
| `:Role` | auth.auth_user_roles | role, is_active |

### Marketing & Notifications

| Node | Source | Key Properties |
|------|--------|----------------|
| `:Lead` | marketing.leads | phone, name, source, utm_source/medium/campaign, status |
| `:Notification` | notifications.notifications | event_type, channel, priority, is_read |

---

## Relationships

### Identity Links
```cypher
// Customer identity chain
(:Customer)-[:HAS_AUTH {via: 'x_auth_id'}]->(:AuthUser)
(:Customer)-[:HAS_WALLET {via: 'customer_id=user_id'}]->(:CustomerWallet)
(:Customer)-[:HAS_PROFILE]->(:CustomerProfile)

// Guide identity chain
(:Guide)-[:HAS_AUTH {via: 'x_auth_id'}]->(:AuthUser)
(:Guide)-[:HAS_WALLET {via: 'id=consultant_id'}]->(:GuideWallet)
```

### Guide Profile
```cypher
(:Guide)-[:HAS_SKILL]->(:Skill)
(:Guide)-[:SPEAKS]->(:Language)
(:Guide)-[:HAS_BANK_ACCOUNT]->(:BankAccount)
(:Guide)-[:HAS_VERIFICATION]->(:Verification)
(:Guide)-[:HAS_SAVED_MESSAGE]->(:SavedMessage)
(:Guide)-[:REFERRED_BY {via: 'referrer_code'}]->(:Guide)
```

### Consultation Flow
```cypher
(:Customer)-[:BOOKED]->(:Consultation)
(:Consultation)-[:WITH_GUIDE]->(:Guide)
(:Consultation)-[:HAS_SESSION]->(:AgoraSession)
(:Consultation)-[:HAS_FEEDBACK]->(:Feedback)
(:Consultation)-[:HAS_METRICS]->(:QualityMetrics)
(:Consultation)-[:PAID_VIA]->(:WalletOrder)
```

### Money Flow
```cypher
// Payment -> Wallet
(:Customer)-[:MADE_PAYMENT]->(:Payment)
(:Payment)-[:VIA_GATEWAY]->(:PaymentGateway)
(:Payment)-[:CREDITED_TO]->(:CustomerWallet)
(:Payment)-[:HAS_INVOICE]->(:Invoice)
(:Payment)-[:MATCHED_RULE]->(:PromotionRule)

// Consultation Payment
(:WalletOrder)-[:DEBITED_FROM]->(:CustomerWallet)
(:WalletOrder)-[:CREDITED_TO]->(:GuideWallet)
(:WalletOrder)-[:FOR_CONSULTATION]->(:Consultation)

// Transactions
(:CustomerWallet)-[:HAS_TRANSACTION]->(:Transaction)
(:Transaction)-[:FOR_ORDER]->(:WalletOrder)
```

### Offers Flow
```cypher
(:Customer)-[:RESERVED]->(:OfferReservation)
(:OfferReservation)-[:FOR_OFFER]->(:Offer)
(:OfferReservation)-[:USED_IN]->(:Consultation)

(:Customer)-[:CONSUMED]->(:OfferConsumption)
(:OfferConsumption)-[:OF_OFFER]->(:Offer)
(:OfferConsumption)-[:VIA_PAYMENT]->(:Payment)

(:Customer)-[:HAS_BEHAVIOR]->(:UserBehavior)
(:Customer)-[:HAS_MILESTONE]->(:MilestoneProgress)
(:MilestoneProgress)-[:FOR_OFFER]->(:Offer)
```

### Auth Flow
```cypher
(:AuthUser)-[:HAS_ROLE]->(:Role)
(:AuthUser)-[:HAS_SESSION]->(:Session)
(:AuthUser)-[:HAS_DEVICE]->(:Device)
(:AuthUser)-[:LOGIN]->(:LoginActivity)
(:AuthUser)-[:OTP]->(:OTPAttempt)
(:Session)-[:ON_DEVICE]->(:Device)
```

### Notifications
```cypher
(:Notification)-[:TO_USER {target_type: 'customer'|'guide'}]->(:AuthUser)
```

### Marketing
```cypher
(:Lead)-[:CONVERTED_TO]->(:Customer)
```

---

## Unused/Empty Tables (Skip)

These tables have no recent data:
- `customers.address`, `customers.customer_address` (feature not used)
- `guide.addresses`, `guide.media`, `guide.agreement`, `guide.kyc_document`
- `consultation.agora_webhook_events`, `consultation.feedback_comments_by_guide`
- `wallet.users`, `wallet.wallets`, `wallet.coupons`, `wallet.quick_connect_rates`
- `wallet.refund_audit`, `wallet.wallet_settings`, `wallet.consultant_payouts`
- `offers.offer_campaigns`, `offers.consultant_rates`, `offers.user_segments`, `offers.volume_bonus_tracking`
- `notifications.client_events`, `notifications.delivery_attempts`, `notifications.escalation_rules`

---

## Sample Cypher Queries

### 1. Full Customer Journey
```cypher
MATCH (c:Customer {phone_number: $phone})
MATCH (c)-[:HAS_AUTH]->(auth:AuthUser)
MATCH (c)-[:HAS_WALLET]->(w:CustomerWallet)
OPTIONAL MATCH (c)-[:BOOKED]->(consult:Consultation)-[:WITH_GUIDE]->(g:Guide)
OPTIONAL MATCH (c)-[:MADE_PAYMENT]->(p:Payment)
RETURN c, auth, w,
       collect(DISTINCT {consultation: consult.id, guide: g.full_name, mode: consult.mode}) as consultations,
       count(DISTINCT p) as payment_count
```

### 2. Guide Earnings
```cypher
MATCH (g:Guide)-[:HAS_WALLET]->(gw:GuideWallet)
MATCH (wo:WalletOrder)-[:CREDITED_TO]->(gw)
WHERE wo.status = 'COMPLETED'
RETURN g.full_name, sum(wo.consultant_share) as total_earnings, count(wo) as orders
ORDER BY total_earnings DESC
```

### 3. Payment to Consultation Flow
```cypher
MATCH (c:Customer)-[:MADE_PAYMENT]->(p:Payment)
MATCH (c)-[:HAS_WALLET]->(cw:CustomerWallet)
MATCH (cw)-[:HAS_TRANSACTION]->(t:Transaction {type: 'SPENT'})
MATCH (t)-[:FOR_ORDER]->(wo:WalletOrder)
MATCH (wo)-[:FOR_CONSULTATION]->(consult:Consultation)
WHERE p.payment_order_id = $payment_id
RETURN c.phone_number, p.amount, wo.final_amount, consult.mode, consult.state
```

### 4. Offer Effectiveness
```cypher
MATCH (o:Offer)<-[:FOR_OFFER]-(res:OfferReservation)<-[:RESERVED]-(c:Customer)
OPTIONAL MATCH (c)-[:CONSUMED]->(cons:OfferConsumption)-[:OF_OFFER]->(o)
RETURN o.offer_name, o.offer_type,
       count(DISTINCT res) as reservations,
       count(DISTINCT cons) as consumptions,
       round(100.0 * count(DISTINCT cons) / count(DISTINCT res), 1) as conversion_rate
ORDER BY reservations DESC
```

### 5. Session/Device Analysis
```cypher
MATCH (auth:AuthUser)-[:HAS_SESSION]->(s:Session)-[:ON_DEVICE]->(d:Device)
WHERE s.is_active = true
RETURN d.platform, d.device_type, count(DISTINCT auth) as active_users
```

---

## Import Order

1. **Reference Data**: Skill, Language, PaymentGateway, PromotionRule, Offer
2. **Auth**: AuthUser, Role
3. **Identities**: Customer, Guide, CustomerProfile
4. **Wallets**: CustomerWallet, GuideWallet
5. **Guide Details**: guide_skills, guide_languages, BankAccount, Verification
6. **Consultations**: Consultation, AgoraSession, Feedback, QualityMetrics
7. **Financial**: Payment, WalletOrder, Transaction, Invoice
8. **Offers**: OfferReservation, OfferConsumption, UserBehavior, MilestoneProgress
9. **Auth Details**: Session, Device, LoginActivity, OTPAttempt
10. **Other**: Lead, Notification

---

## Notes

1. **ID Matching**: `Customer.customer_id` = `UserWallet.user_id`, `Guide.id` = `ConsultantWallet.consultant_id`
2. **Phone Linking**: Used as backup link between Guide and wallet tables
3. **x_auth_id**: Links both Customer and Guide to AuthUser
4. **Notification target**: Uses `auth_user_id` as string + `target_type` to identify customer/guide
5. **Legacy Tables**: `wallet.consultants`, `wallet.users`, `wallet.wallets` appear to be deprecated
