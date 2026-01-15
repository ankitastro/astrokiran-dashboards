--
-- PostgreSQL database dump
--

\restrict wfHwuW3ZIxLGrE7uPMjnfe3DGZLdkvKQN9Ak5eY6oIL0WWGUHZUudL8a9tRvI2S

-- Dumped from database version 15.12
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: admin; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA admin;


ALTER SCHEMA admin OWNER TO postgres;

--
-- Name: audit; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA audit;


ALTER SCHEMA audit OWNER TO postgres;

--
-- Name: auth; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA auth;


ALTER SCHEMA auth OWNER TO postgres;

--
-- Name: consultation; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA consultation;


ALTER SCHEMA consultation OWNER TO postgres;

--
-- Name: customers; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA customers;


ALTER SCHEMA customers OWNER TO postgres;

--
-- Name: guide; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA guide;


ALTER SCHEMA guide OWNER TO postgres;

--
-- Name: marketing; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA marketing;


ALTER SCHEMA marketing OWNER TO postgres;

--
-- Name: notifications; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA notifications;


ALTER SCHEMA notifications OWNER TO postgres;

--
-- Name: offers; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA offers;


ALTER SCHEMA offers OWNER TO postgres;

--
-- Name: wallet; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA wallet;


ALTER SCHEMA wallet OWNER TO postgres;

--
-- Name: audit_action_enum; Type: TYPE; Schema: admin; Owner: postgres
--

CREATE TYPE admin.audit_action_enum AS ENUM (
    'CREATE',
    'UPDATE',
    'DELETE',
    'VERIFY',
    'REJECT',
    'APPROVE',
    'SUSPEND',
    'ACTIVATE',
    'ADMIN_CHECK'
);


ALTER TYPE admin.audit_action_enum OWNER TO postgres;

--
-- Name: resource_type_enum; Type: TYPE; Schema: admin; Owner: postgres
--

CREATE TYPE admin.resource_type_enum AS ENUM (
    'ADMIN_USER',
    'CUSTOMER',
    'GUIDE',
    'CONSULTATION',
    'ORDER',
    'TRANSACTION',
    'VERIFICATION',
    'SYSTEM'
);


ALTER TYPE admin.resource_type_enum OWNER TO postgres;

--
-- Name: agora_event_type; Type: TYPE; Schema: consultation; Owner: postgres
--

CREATE TYPE consultation.agora_event_type AS ENUM (
    'channel_created',
    'channel_destroyed',
    'broadcaster_joined_channel',
    'broadcaster_left_channel',
    'audience_joined_channel',
    'audience_left_channel',
    'client_role_changed_to_broadcaster',
    'client_role_changed_to_audience',
    'communication_mode_user_join_channel',
    'communication_mode_user_leave_channel',
    'client_upstream_changes'
);


ALTER TYPE consultation.agora_event_type OWNER TO postgres;

--
-- Name: cancellation_reason; Type: TYPE; Schema: consultation; Owner: postgres
--

CREATE TYPE consultation.cancellation_reason AS ENUM (
    'not_interested',
    'change_guide',
    'other'
);


ALTER TYPE consultation.cancellation_reason OWNER TO postgres;

--
-- Name: consultation_category; Type: TYPE; Schema: consultation; Owner: postgres
--

CREATE TYPE consultation.consultation_category AS ENUM (
    'astrology',
    'tarot',
    'palmistry',
    'numerology',
    'prashan_kundali',
    'vedic',
    'face_reading',
    'crystal_healing',
    'reiki',
    'dream_analysis'
);


ALTER TYPE consultation.consultation_category OWNER TO postgres;

--
-- Name: consultation_mode; Type: TYPE; Schema: consultation; Owner: postgres
--

CREATE TYPE consultation.consultation_mode AS ENUM (
    'voice',
    'video',
    'chat'
);


ALTER TYPE consultation.consultation_mode OWNER TO postgres;

--
-- Name: consultation_session_status; Type: TYPE; Schema: consultation; Owner: postgres
--

CREATE TYPE consultation.consultation_session_status AS ENUM (
    'guide_initiated',
    'user_joined',
    'user_rejected',
    'guide_dropped',
    'customer_dropped',
    'call_complete',
    'network_abandoned',
    'customer_join_timeout'
);


ALTER TYPE consultation.consultation_session_status OWNER TO postgres;

--
-- Name: consultation_state; Type: TYPE; Schema: consultation; Owner: postgres
--

CREATE TYPE consultation.consultation_state AS ENUM (
    'requested',
    'in_progress',
    'completed',
    'cancelled',
    'failed',
    'request_expired',
    'request_cancelled',
    'guide_accept_timeout',
    'request_join_timeout',
    'billing_failed',
    'call_completed',
    'started',
    'guide_rejected',
    'customer_rejected',
    'guide_accepted',
    'customer_join_timeout'
);


ALTER TYPE consultation.consultation_state OWNER TO postgres;

--
-- Name: feedback_status; Type: TYPE; Schema: consultation; Owner: postgres
--

CREATE TYPE consultation.feedback_status AS ENUM (
    'submitted',
    'visible',
    'reported',
    'under_review',
    'resolved',
    'rejected'
);


ALTER TYPE consultation.feedback_status OWNER TO postgres;

--
-- Name: agreement_status_enum; Type: TYPE; Schema: guide; Owner: postgres
--

CREATE TYPE guide.agreement_status_enum AS ENUM (
    'generated',
    'shared',
    'signed',
    'expired',
    'revoked'
);


ALTER TYPE guide.agreement_status_enum OWNER TO postgres;

--
-- Name: document_type_enum; Type: TYPE; Schema: guide; Owner: postgres
--

CREATE TYPE guide.document_type_enum AS ENUM (
    'aadhaar',
    'pan',
    'voter_id',
    'driving_license',
    'passport',
    'birth_certificate',
    'marksheet',
    'appointment_letter',
    'experience_letter',
    'other'
);


ALTER TYPE guide.document_type_enum OWNER TO postgres;

--
-- Name: kyc_document_status_enum; Type: TYPE; Schema: guide; Owner: postgres
--

CREATE TYPE guide.kyc_document_status_enum AS ENUM (
    'uploaded',
    'verified',
    'rejected'
);


ALTER TYPE guide.kyc_document_status_enum OWNER TO postgres;

--
-- Name: onboarding_state_enum; Type: TYPE; Schema: guide; Owner: postgres
--

CREATE TYPE guide.onboarding_state_enum AS ENUM (
    'REGISTRATION_PENDING',
    'KYC_PENDING',
    'KYC_UPLOADED',
    'KYC_VERIFIED',
    'KYC_FAILED',
    'AGREEMENT_SENT',
    'AGREEMENT_EXPIRED',
    'AGREEMENT_SIGNED',
    'ONBOARDING_CONTENT_PENDING',
    'ACTIVE',
    'GUIDE_OFFBOARDED'
);


ALTER TYPE guide.onboarding_state_enum OWNER TO postgres;

--
-- Name: verification_status_enum; Type: TYPE; Schema: guide; Owner: postgres
--

CREATE TYPE guide.verification_status_enum AS ENUM (
    'uploaded',
    'verified',
    'rejected'
);


ALTER TYPE guide.verification_status_enum OWNER TO postgres;

--
-- Name: verification_target_enum; Type: TYPE; Schema: guide; Owner: postgres
--

CREATE TYPE guide.verification_target_enum AS ENUM (
    'KYC_DOCUMENT',
    'BANK_ACCOUNT',
    'AGREEMENT',
    'EDUCATION',
    'EMPLOYMENT'
);


ALTER TYPE guide.verification_target_enum OWNER TO postgres;

--
-- Name: user_segment_type; Type: TYPE; Schema: offers; Owner: postgres
--

CREATE TYPE offers.user_segment_type AS ENUM (
    'RECONCILIATION_USER'
);


ALTER TYPE offers.user_segment_type OWNER TO postgres;

--
-- Name: coupon_type; Type: TYPE; Schema: wallet; Owner: postgres
--

CREATE TYPE wallet.coupon_type AS ENUM (
    'FREE_MINUTES',
    'PERCENTAGE_OFF',
    'FIXED_AMOUNT_OFF'
);


ALTER TYPE wallet.coupon_type OWNER TO postgres;

--
-- Name: order_status; Type: TYPE; Schema: wallet; Owner: postgres
--

CREATE TYPE wallet.order_status AS ENUM (
    'PENDING',
    'INPROGRESS',
    'COMPLETED',
    'REFUNDED',
    'CANCELLED'
);


ALTER TYPE wallet.order_status OWNER TO postgres;

--
-- Name: payment_method; Type: TYPE; Schema: wallet; Owner: postgres
--

CREATE TYPE wallet.payment_method AS ENUM (
    'WALLET',
    'BANK_TRANSFER',
    'CASH'
);


ALTER TYPE wallet.payment_method OWNER TO postgres;

--
-- Name: payment_methods; Type: TYPE; Schema: wallet; Owner: postgres
--

CREATE TYPE wallet.payment_methods AS ENUM (
    'UPI',
    'UPI_QR',
    'NEFT',
    'RTGS',
    'DEBIT_CARD',
    'CREDIT_CARD',
    'EXTERNAL'
);


ALTER TYPE wallet.payment_methods OWNER TO postgres;

--
-- Name: payment_order_status; Type: TYPE; Schema: wallet; Owner: postgres
--

CREATE TYPE wallet.payment_order_status AS ENUM (
    'PENDING',
    'SUCCESSFUL',
    'FAILED',
    'EXPIRED'
);


ALTER TYPE wallet.payment_order_status OWNER TO postgres;

--
-- Name: payout_status; Type: TYPE; Schema: wallet; Owner: postgres
--

CREATE TYPE wallet.payout_status AS ENUM (
    'PENDING',
    'PAID',
    'FAILED'
);


ALTER TYPE wallet.payout_status OWNER TO postgres;

--
-- Name: refund_status; Type: TYPE; Schema: wallet; Owner: postgres
--

CREATE TYPE wallet.refund_status AS ENUM (
    'INITIATED',
    'PROCESSING',
    'COMPLETED',
    'FAILED',
    'CANCELLED'
);


ALTER TYPE wallet.refund_status OWNER TO postgres;

--
-- Name: service_type; Type: TYPE; Schema: wallet; Owner: postgres
--

CREATE TYPE wallet.service_type AS ENUM (
    'CHAT',
    'CALL',
    'REPORT',
    'PRODUCT'
);


ALTER TYPE wallet.service_type OWNER TO postgres;

--
-- Name: transaction_type; Type: TYPE; Schema: wallet; Owner: postgres
--

CREATE TYPE wallet.transaction_type AS ENUM (
    'ADD',
    'SPENT',
    'CB_1MIN',
    'REFUND',
    'INITIAL_PAYMENT',
    'ADJUSTMENT',
    'PROMOTIONAL',
    'PROMOTION_GRANT'
);


ALTER TYPE wallet.transaction_type OWNER TO postgres;

--
-- Name: if_modified_func(); Type: FUNCTION; Schema: audit; Owner: postgres
--

CREATE FUNCTION audit.if_modified_func() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog', 'audit'
    AS $$
    DECLARE
        v_old_data JSONB;
        v_new_data JSONB;
    BEGIN
        IF (TG_OP = 'UPDATE') THEN
            v_old_data := TO_JSONB(OLD.*);
            v_new_data := TO_JSONB(NEW.*);
            INSERT INTO audit.logged_actions (schema_name, table_name, user_name, action, original_data, new_data, query)
            VALUES (TG_TABLE_SCHEMA::TEXT, TG_TABLE_NAME::TEXT, session_user::TEXT, substring(TG_OP,1,1), v_old_data, v_new_data, current_query());
            RETURN NEW;
        ELSIF (TG_OP = 'DELETE') THEN
            v_old_data := TO_JSONB(OLD.*);
            INSERT INTO audit.logged_actions (schema_name, table_name, user_name, action, original_data, query)
            VALUES (TG_TABLE_SCHEMA::TEXT, TG_TABLE_NAME::TEXT, session_user::TEXT, substring(TG_OP,1,1), v_old_data, current_query());
            RETURN OLD;
        ELSIF (TG_OP = 'INSERT') THEN
            v_new_data := TO_JSONB(NEW.*);
            INSERT INTO audit.logged_actions (schema_name, table_name, user_name, action, new_data, query)
            VALUES (TG_TABLE_SCHEMA::TEXT, TG_TABLE_NAME::TEXT, session_user::TEXT, substring(TG_OP,1,1), v_new_data, current_query());
            RETURN NEW;
        ELSE
            RAISE WARNING '[AUDIT.IF_MODIFIED_FUNC] - Other action occurred: %, at %', TG_OP, now();
            RETURN NULL;
        END IF;

    EXCEPTION
        WHEN data_exception THEN
            RAISE WARNING '[AUDIT.IF_MODIFIED_FUNC] - UDF ERROR [DATA EXCEPTION] - SQLSTATE: %, SQLERRM: %', SQLSTATE, SQLERRM;
            RETURN NULL;
        WHEN unique_violation THEN
            RAISE WARNING '[AUDIT.IF_MODIFIED_FUNC] - UDF ERROR [UNIQUE] - SQLSTATE: %, SQLERRM: %', SQLSTATE, SQLERRM;
            RETURN NULL;
        WHEN OTHERS THEN
            RAISE WARNING '[AUDIT.IF_MODIFIED_FUNC] - UDF ERROR [OTHER] - SQLSTATE: %, SQLERRM: %', SQLSTATE, SQLERRM;
            RETURN NULL;
    END;
    $$;


ALTER FUNCTION audit.if_modified_func() OWNER TO postgres;

--
-- Name: cleanup_old_data(); Type: FUNCTION; Schema: consultation; Owner: postgres
--

CREATE FUNCTION consultation.cleanup_old_data() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete webhook events older than 30 days
    DELETE FROM consultation.agora_webhook_events
    WHERE created_at < NOW() - INTERVAL '30 days';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- Soft delete old completed consultations (older than 2 years)
    UPDATE consultation.consultation
    SET deleted_at = NOW()
    WHERE state IN ('completed', 'cancelled', 'failed')
    AND created_at < NOW() - INTERVAL '2 years'
    AND deleted_at IS NULL;

    RETURN deleted_count;
END;
$$;


ALTER FUNCTION consultation.cleanup_old_data() OWNER TO postgres;

--
-- Name: increment_version(); Type: FUNCTION; Schema: consultation; Owner: postgres
--

CREATE FUNCTION consultation.increment_version() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.version = OLD.version + 1;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION consultation.increment_version() OWNER TO postgres;

--
-- Name: update_session_duration(); Type: FUNCTION; Schema: consultation; Owner: postgres
--

CREATE FUNCTION consultation.update_session_duration() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.end_time IS NOT NULL AND OLD.end_time IS NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION consultation.update_session_duration() OWNER TO postgres;

--
-- Name: set_updated_at(); Type: FUNCTION; Schema: guide; Owner: postgres
--

CREATE FUNCTION guide.set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$;


ALTER FUNCTION guide.set_updated_at() OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: notifications; Owner: postgres
--

CREATE FUNCTION notifications.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION notifications.update_updated_at_column() OWNER TO postgres;

--
-- Name: calculate_offer_value(uuid, numeric, text[]); Type: FUNCTION; Schema: offers; Owner: postgres
--

CREATE FUNCTION offers.calculate_offer_value(p_offer_id uuid, p_amount numeric, p_guide_tiers text[]) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_def RECORD;
    v_value DECIMAL := 0;
    v_eligible BOOLEAN := false;
BEGIN
    SELECT * INTO v_def FROM offers.offer_definitions WHERE offer_id = p_offer_id;
    IF NOT FOUND THEN RETURN 0; END IF;

    -- Check guide tier eligibility (if applicable)
    IF v_def.target_guide_tiers IS NULL OR array_length(v_def.target_guide_tiers, 1) = 0 THEN
        v_eligible := true;
    ELSE
        SELECT EXISTS (
            SELECT 1 FROM unnest(v_def.target_guide_tiers) AS tier
            WHERE tier = ANY(p_guide_tiers)
        ) INTO v_eligible;
    END IF;

    IF NOT v_eligible THEN RETURN 0; END IF;

    CASE v_def.offer_category
        WHEN 'FREE_MINUTES' THEN v_value := COALESCE(v_def.bonus_fixed_amount, 0);
        WHEN 'PERCENTAGE_DISCOUNT' THEN v_value := p_amount * (COALESCE(v_def.bonus_percentage, 0) / 100);
        WHEN 'FIXED_AMOUNT_DISCOUNT' THEN v_value := COALESCE(v_def.bonus_fixed_amount, 0);
        ELSE v_value := 0;
    END CASE;

    RETURN v_value;
END;
$$;


ALTER FUNCTION offers.calculate_offer_value(p_offer_id uuid, p_amount numeric, p_guide_tiers text[]) OWNER TO postgres;

--
-- Name: set_consumption_timestamp(); Type: FUNCTION; Schema: offers; Owner: postgres
--

CREATE FUNCTION offers.set_consumption_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.consumed_at IS NULL THEN
        NEW.consumed_at = NOW();
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION offers.set_consumption_timestamp() OWNER TO postgres;

--
-- Name: track_consultation(bigint, numeric, integer, character varying); Type: FUNCTION; Schema: offers; Owner: postgres
--

CREATE FUNCTION offers.track_consultation(p_user_id bigint, p_amount numeric, p_duration integer, p_service_type character varying) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE offers.user_behavior_metrics
    SET
        total_consultations = COALESCE(total_consultations, 0) + 1,
        total_spent = COALESCE(total_spent, 0.00) + p_amount,
        total_quick_connect_consultations = COALESCE(total_quick_connect_consultations, 0) +
            CASE WHEN p_service_type = 'QUICK_CONNECT' THEN 1 ELSE 0 END,
        average_consultation_duration =
            CASE
                WHEN total_consultations = 0 THEN p_duration
                ELSE ((COALESCE(average_consultation_duration, 0) * total_consultations) + p_duration) / (total_consultations + 1)
            END,
        preferred_service_type =
            CASE
                WHEN preferred_service_type IS NULL THEN p_service_type
                WHEN p_service_type = preferred_service_type THEN preferred_service_type
                ELSE 'MIXED'
            END,
        last_consultation_at = NOW(),
        last_activity_at = NOW(),
        updated_at = NOW()
    WHERE user_id = p_user_id;

    IF NOT FOUND THEN
        INSERT INTO offers.user_behavior_metrics (
            user_id, total_consultations, total_spent, average_consultation_duration,
            preferred_service_type, last_consultation_at, last_activity_at, user_segment
        ) VALUES (
            p_user_id, 1, p_amount, p_duration, p_service_type, NOW(), NOW(), 'NEW'
        );
    END IF;
END;
$$;


ALTER FUNCTION offers.track_consultation(p_user_id bigint, p_amount numeric, p_duration integer, p_service_type character varying) OWNER TO postgres;

--
-- Name: FUNCTION track_consultation(p_user_id bigint, p_amount numeric, p_duration integer, p_service_type character varying); Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON FUNCTION offers.track_consultation(p_user_id bigint, p_amount numeric, p_duration integer, p_service_type character varying) IS 'Tracks consultation activity and updates user behavior metrics';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: offers; Owner: postgres
--

CREATE FUNCTION offers.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION offers.update_updated_at_column() OWNER TO postgres;

--
-- Name: update_user_segment(); Type: FUNCTION; Schema: offers; Owner: postgres
--

CREATE FUNCTION offers.update_user_segment() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    total_consultations INTEGER;
    total_spent DECIMAL(15,2);
    last_activity_days INTEGER;
    is_first_time BOOLEAN;
BEGIN
    total_consultations := COALESCE(NEW.total_consultations, 0);
    total_spent := COALESCE(NEW.total_spent, 0.00);
    is_first_time := COALESCE(NEW.is_first_time_user, true);

    IF NEW.last_activity_at IS NOT NULL THEN
        last_activity_days := EXTRACT(DAY FROM (NOW() - NEW.last_activity_at));
    ELSE
        last_activity_days := 999;
    END IF;

    IF is_first_time AND NEW.first_recharge_at IS NULL THEN
        NEW.user_segment := 'NEW';
    ELSIF total_consultations >= 10 AND total_spent >= 1000.00 THEN
        NEW.user_segment := 'VIP';
    ELSIF total_consultations >= 5 AND total_spent >= 500.00 THEN
        NEW.user_segment := 'LOYAL';
    ELSIF last_activity_days <= 30 AND total_consultations >= 2 THEN
        NEW.user_segment := 'ENGAGED';
    ELSIF last_activity_days > 60 AND total_consultations = 0 THEN
        NEW.user_segment := 'AT_RISK';
    ELSE
        NEW.user_segment := 'NEW';
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION offers.update_user_segment() OWNER TO postgres;

--
-- Name: FUNCTION update_user_segment(); Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON FUNCTION offers.update_user_segment() IS 'Automatically calculates user segment based on behavior metrics';


--
-- Name: jsonb_diff_val(jsonb, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.jsonb_diff_val(val1 jsonb, val2 jsonb) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
    DECLARE
        result JSONB;
        v RECORD;
    BEGIN
        result = val1;
        FOR v IN SELECT * FROM jsonb_each(val2) LOOP
            IF result @> jsonb_build_object(v.key, v.value)
                THEN result = result - v.key;
            ELSIF result ? v.key THEN CONTINUE;
            ELSE
                result = result || jsonb_build_object(v.key, 'null');
            END IF;
        END LOOP;
        RETURN result;
    END;
    $$;


ALTER FUNCTION public.jsonb_diff_val(val1 jsonb, val2 jsonb) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_users; Type: TABLE; Schema: admin; Owner: postgres
--

CREATE TABLE admin.admin_users (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    phone_number character varying(20) NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    is_active boolean NOT NULL,
    department character varying(100),
    notes text,
    created_by_phone character varying(20),
    updated_by_phone character varying(20),
    job_title character varying(100)
);


ALTER TABLE admin.admin_users OWNER TO postgres;

--
-- Name: COLUMN admin_users.created_at; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.created_at IS 'Record creation timestamp';


--
-- Name: COLUMN admin_users.updated_at; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.updated_at IS 'Record last update timestamp';


--
-- Name: COLUMN admin_users.phone_number; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.phone_number IS 'Admin user phone number (used for OTP login via auth-gateway)';


--
-- Name: COLUMN admin_users.name; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.name IS 'Full name of the admin user';


--
-- Name: COLUMN admin_users.email; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.email IS 'Admin user email address';


--
-- Name: COLUMN admin_users.is_active; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.is_active IS 'Whether the admin account is active';


--
-- Name: COLUMN admin_users.department; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.department IS 'Department or team the admin belongs to';


--
-- Name: COLUMN admin_users.notes; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.notes IS 'Internal notes about the admin user';


--
-- Name: COLUMN admin_users.created_by_phone; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.created_by_phone IS 'Phone number of admin who created this account';


--
-- Name: COLUMN admin_users.updated_by_phone; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.updated_by_phone IS 'Phone number of admin who last updated this account';


--
-- Name: COLUMN admin_users.job_title; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.admin_users.job_title IS 'Official job title of the admin user';


--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: admin; Owner: postgres
--

CREATE SEQUENCE admin.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE admin.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: admin; Owner: postgres
--

ALTER SEQUENCE admin.admin_users_id_seq OWNED BY admin.admin_users.id;


--
-- Name: alembic_version; Type: TABLE; Schema: admin; Owner: postgres
--

CREATE TABLE admin.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE admin.alembic_version OWNER TO postgres;

--
-- Name: audit_logs; Type: TABLE; Schema: admin; Owner: postgres
--

CREATE TABLE admin.audit_logs (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    action character varying(100) NOT NULL,
    resource_type character varying(50) NOT NULL,
    resource_id character varying(100),
    admin_user_id integer,
    admin_username character varying(50) NOT NULL,
    session_id character varying(255),
    ip_address inet,
    user_agent text,
    request_id character varying(100),
    endpoint character varying(255),
    http_method character varying(10),
    status_code integer,
    old_values json,
    new_values json,
    request_data json,
    description text,
    tags json,
    log_metadata json,
    success boolean NOT NULL,
    error_message text,
    error_code character varying(50),
    duration_ms integer,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    retention_until timestamp with time zone
);


ALTER TABLE admin.audit_logs OWNER TO postgres;

--
-- Name: COLUMN audit_logs.created_at; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.created_at IS 'Record creation timestamp';


--
-- Name: COLUMN audit_logs.updated_at; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.updated_at IS 'Record last update timestamp';


--
-- Name: COLUMN audit_logs.action; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.action IS 'Type of action performed (CREATE_USER, UPDATE_CUSTOMER, etc.)';


--
-- Name: COLUMN audit_logs.resource_type; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.resource_type IS 'Type of resource affected (CUSTOMER, GUIDE, CONSULTATION, etc.)';


--
-- Name: COLUMN audit_logs.resource_id; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.resource_id IS 'ID of the affected resource';


--
-- Name: COLUMN audit_logs.admin_user_id; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.admin_user_id IS 'ID of the admin user who performed the action';


--
-- Name: COLUMN audit_logs.admin_username; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.admin_username IS 'Username of the admin user (for quick reference)';


--
-- Name: COLUMN audit_logs.session_id; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.session_id IS 'Session ID when the action was performed';


--
-- Name: COLUMN audit_logs.ip_address; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.ip_address IS 'IP address from which the action was performed';


--
-- Name: COLUMN audit_logs.user_agent; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.user_agent IS 'User agent string of the client';


--
-- Name: COLUMN audit_logs.request_id; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.request_id IS 'Unique request ID for tracing';


--
-- Name: COLUMN audit_logs.endpoint; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.endpoint IS 'API endpoint that was called';


--
-- Name: COLUMN audit_logs.http_method; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.http_method IS 'HTTP method used (GET, POST, PUT, DELETE)';


--
-- Name: COLUMN audit_logs.status_code; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.status_code IS 'HTTP status code of the response';


--
-- Name: COLUMN audit_logs.old_values; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.old_values IS 'Previous values before the change (for updates/deletes)';


--
-- Name: COLUMN audit_logs.new_values; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.new_values IS 'New values after the change (for creates/updates)';


--
-- Name: COLUMN audit_logs.request_data; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.request_data IS 'Request payload data';


--
-- Name: COLUMN audit_logs.description; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.description IS 'Human-readable description of the action';


--
-- Name: COLUMN audit_logs.tags; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.tags IS 'Additional tags for categorization and filtering';


--
-- Name: COLUMN audit_logs.log_metadata; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.log_metadata IS 'Additional metadata about the action';


--
-- Name: COLUMN audit_logs.success; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.success IS 'Whether the action was successful';


--
-- Name: COLUMN audit_logs.error_message; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.error_message IS 'Error message if the action failed';


--
-- Name: COLUMN audit_logs.error_code; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.error_code IS 'Error code if the action failed';


--
-- Name: COLUMN audit_logs.duration_ms; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.duration_ms IS 'Duration of the action in milliseconds';


--
-- Name: COLUMN audit_logs."timestamp"; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs."timestamp" IS 'Timestamp when the action occurred';


--
-- Name: COLUMN audit_logs.retention_until; Type: COMMENT; Schema: admin; Owner: postgres
--

COMMENT ON COLUMN admin.audit_logs.retention_until IS 'Date until which this log should be retained';


--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: admin; Owner: postgres
--

CREATE SEQUENCE admin.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE admin.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: admin; Owner: postgres
--

ALTER SEQUENCE admin.audit_logs_id_seq OWNED BY admin.audit_logs.id;


--
-- Name: logged_actions; Type: TABLE; Schema: audit; Owner: postgres
--

CREATE TABLE audit.logged_actions (
    schema_name text NOT NULL,
    table_name text NOT NULL,
    user_name text,
    action_tstamp timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    action text NOT NULL,
    original_data jsonb,
    new_data jsonb,
    query text,
    CONSTRAINT logged_actions_action_check CHECK ((action = ANY (ARRAY['I'::text, 'D'::text, 'U'::text])))
)
WITH (fillfactor='100');


ALTER TABLE audit.logged_actions OWNER TO postgres;

--
-- Name: auth_user_roles; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.auth_user_roles (
    id bigint NOT NULL,
    auth_user_id bigint NOT NULL,
    role character varying(20) NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE auth.auth_user_roles OWNER TO postgres;

--
-- Name: auth_user_roles_id_seq; Type: SEQUENCE; Schema: auth; Owner: postgres
--

CREATE SEQUENCE auth.auth_user_roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.auth_user_roles_id_seq OWNER TO postgres;

--
-- Name: auth_user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: postgres
--

ALTER SEQUENCE auth.auth_user_roles_id_seq OWNED BY auth.auth_user_roles.id;


--
-- Name: auth_users; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.auth_users (
    id bigint NOT NULL,
    area_code character varying(5) NOT NULL,
    phone_number character varying(15) NOT NULL,
    full_phone text NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone,
    is_test_user boolean DEFAULT false NOT NULL
);


ALTER TABLE auth.auth_users OWNER TO postgres;

--
-- Name: COLUMN auth_users.is_test_user; Type: COMMENT; Schema: auth; Owner: postgres
--

COMMENT ON COLUMN auth.auth_users.is_test_user IS 'Flag indicating if this user is a test user. Test users see test guides and have special filtering applied.';


--
-- Name: auth_users_id_seq; Type: SEQUENCE; Schema: auth; Owner: postgres
--

CREATE SEQUENCE auth.auth_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.auth_users_id_seq OWNER TO postgres;

--
-- Name: auth_users_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: postgres
--

ALTER SEQUENCE auth.auth_users_id_seq OWNED BY auth.auth_users.id;


--
-- Name: casbin_rules; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.casbin_rules (
    id bigint NOT NULL,
    ptype character varying(100),
    v0 character varying(100),
    v1 character varying(100),
    v2 character varying(100),
    v3 character varying(100),
    v4 character varying(100),
    v5 character varying(100)
);


ALTER TABLE auth.casbin_rules OWNER TO postgres;

--
-- Name: casbin_rules_id_seq; Type: SEQUENCE; Schema: auth; Owner: postgres
--

CREATE SEQUENCE auth.casbin_rules_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.casbin_rules_id_seq OWNER TO postgres;

--
-- Name: casbin_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: postgres
--

ALTER SEQUENCE auth.casbin_rules_id_seq OWNED BY auth.casbin_rules.id;


--
-- Name: login_activities; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.login_activities (
    id bigint NOT NULL,
    auth_user_id bigint NOT NULL,
    user_type character varying(20) NOT NULL,
    action character varying(30) NOT NULL,
    device_type character varying(10) NOT NULL,
    ip_address text NOT NULL,
    user_agent text,
    session_id text,
    success boolean NOT NULL,
    fail_reason text,
    metadata text,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT login_activities_device_type_check CHECK (((device_type)::text = ANY (ARRAY[('mobile'::character varying)::text, ('web'::character varying)::text])))
);


ALTER TABLE auth.login_activities OWNER TO postgres;

--
-- Name: login_activities_id_seq; Type: SEQUENCE; Schema: auth; Owner: postgres
--

CREATE SEQUENCE auth.login_activities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.login_activities_id_seq OWNER TO postgres;

--
-- Name: login_activities_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: postgres
--

ALTER SEQUENCE auth.login_activities_id_seq OWNED BY auth.login_activities.id;


--
-- Name: otp_attempts; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.otp_attempts (
    id bigint NOT NULL,
    auth_user_id bigint NOT NULL,
    otp_request_id text NOT NULL,
    otp_code text NOT NULL,
    user_type character varying(20) NOT NULL,
    purpose character varying(20) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    is_used boolean DEFAULT false,
    is_expired boolean DEFAULT false,
    validation_attempts bigint DEFAULT 0,
    max_validation_attempts bigint DEFAULT 3,
    request_count bigint DEFAULT 1,
    max_request_count bigint DEFAULT 3,
    ip_address text NOT NULL,
    user_agent text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE auth.otp_attempts OWNER TO postgres;

--
-- Name: otp_attempts_id_seq; Type: SEQUENCE; Schema: auth; Owner: postgres
--

CREATE SEQUENCE auth.otp_attempts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.otp_attempts_id_seq OWNER TO postgres;

--
-- Name: otp_attempts_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: postgres
--

ALTER SEQUENCE auth.otp_attempts_id_seq OWNED BY auth.otp_attempts.id;


--
-- Name: user_devices; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.user_devices (
    id bigint NOT NULL,
    auth_user_id bigint NOT NULL,
    device_id text NOT NULL,
    device_type character varying(10) NOT NULL,
    device_name character varying(100),
    platform character varying(20),
    platform_version character varying(50),
    app_version character varying(20),
    fcm_token text,
    is_active boolean DEFAULT true,
    last_seen_at timestamp with time zone DEFAULT now() NOT NULL,
    first_seen_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT user_devices_device_type_check CHECK (((device_type)::text = ANY (ARRAY[('mobile'::character varying)::text, ('web'::character varying)::text])))
);


ALTER TABLE auth.user_devices OWNER TO postgres;

--
-- Name: user_devices_id_seq; Type: SEQUENCE; Schema: auth; Owner: postgres
--

CREATE SEQUENCE auth.user_devices_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.user_devices_id_seq OWNER TO postgres;

--
-- Name: user_devices_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: postgres
--

ALTER SEQUENCE auth.user_devices_id_seq OWNED BY auth.user_devices.id;


--
-- Name: user_sessions; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.user_sessions (
    id bigint NOT NULL,
    auth_user_id bigint NOT NULL,
    user_type character varying(20) NOT NULL,
    session_id text NOT NULL,
    device_type character varying(10) NOT NULL,
    device_info text,
    ip_address text NOT NULL,
    user_agent text,
    access_token text NOT NULL,
    refresh_token text NOT NULL,
    access_token_exp timestamp with time zone NOT NULL,
    refresh_token_exp timestamp with time zone NOT NULL,
    is_active boolean DEFAULT true,
    last_accessed_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    device_id text,
    browser_name character varying(50),
    browser_version character varying(20),
    os_name character varying(50),
    os_version character varying(50),
    CONSTRAINT user_sessions_device_type_check CHECK (((device_type)::text = ANY (ARRAY[('mobile'::character varying)::text, ('web'::character varying)::text])))
);


ALTER TABLE auth.user_sessions OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: auth; Owner: postgres
--

CREATE SEQUENCE auth.user_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.user_sessions_id_seq OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: postgres
--

ALTER SEQUENCE auth.user_sessions_id_seq OWNED BY auth.user_sessions.id;


--
-- Name: agora_consultation_session; Type: TABLE; Schema: consultation; Owner: postgres
--

CREATE TABLE consultation.agora_consultation_session (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    consultation_id bigint NOT NULL,
    mode consultation.consultation_mode NOT NULL,
    agora_channel_name character varying(1024) NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    duration_seconds integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    guide_agora_chat_user_id character varying(1024) DEFAULT NULL::character varying,
    customer_agora_chat_user_id character varying(1024) DEFAULT NULL::character varying,
    guide_agora_chat_user_token character varying(1024) DEFAULT NULL::character varying,
    guide_agora_chat_user_token_expires_at timestamp with time zone,
    customer_agora_chat_user_token character varying(1024) DEFAULT NULL::character varying,
    customer_agora_chat_user_token_expires_at timestamp with time zone,
    guide_agora_call_token character varying(1024) DEFAULT NULL::character varying,
    guide_agora_call_token_expires_at timestamp with time zone,
    customer_agora_call_token character varying(1024) DEFAULT NULL::character varying,
    customer_agora_call_token_expires_at timestamp with time zone,
    status consultation.consultation_session_status DEFAULT 'guide_initiated'::consultation.consultation_session_status NOT NULL,
    recording_bot_rtc_token character varying(512),
    recording_bot_rtc_token_expires_at timestamp without time zone,
    guide_agora_rtm_token character varying(512),
    guide_agora_rtm_token_expires_at timestamp without time zone,
    customer_agora_rtm_token character varying(512),
    customer_agora_rtm_token_expires_at timestamp without time zone
);


ALTER TABLE consultation.agora_consultation_session OWNER TO postgres;

--
-- Name: COLUMN agora_consultation_session.recording_bot_rtc_token; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.agora_consultation_session.recording_bot_rtc_token IS 'RTC token for recording bot (UID = consultation_id) used for cloud recording';


--
-- Name: COLUMN agora_consultation_session.recording_bot_rtc_token_expires_at; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.agora_consultation_session.recording_bot_rtc_token_expires_at IS 'Expiration timestamp for recording bot RTC token';


--
-- Name: COLUMN agora_consultation_session.guide_agora_rtm_token; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.agora_consultation_session.guide_agora_rtm_token IS 'RTM (Real-Time Messaging) token for guide used for Agora RTM messaging';


--
-- Name: COLUMN agora_consultation_session.guide_agora_rtm_token_expires_at; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.agora_consultation_session.guide_agora_rtm_token_expires_at IS 'Expiration timestamp for guide RTM token';


--
-- Name: COLUMN agora_consultation_session.customer_agora_rtm_token; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.agora_consultation_session.customer_agora_rtm_token IS 'RTM (Real-Time Messaging) token for customer used for Agora RTM messaging';


--
-- Name: COLUMN agora_consultation_session.customer_agora_rtm_token_expires_at; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.agora_consultation_session.customer_agora_rtm_token_expires_at IS 'Expiration timestamp for customer RTM token';


--
-- Name: agora_webhook_events; Type: TABLE; Schema: consultation; Owner: postgres
--

CREATE TABLE consultation.agora_webhook_events (
    id bigint NOT NULL,
    consultation_session_id uuid NOT NULL,
    channel_name character varying(1024) NOT NULL,
    event_type consultation.agora_event_type NOT NULL,
    app_id character varying(1024) NOT NULL,
    product_id integer NOT NULL,
    url_region character varying(1024) NOT NULL,
    event_timestamp timestamp with time zone,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE consultation.agora_webhook_events OWNER TO postgres;

--
-- Name: agora_webhook_events_id_seq; Type: SEQUENCE; Schema: consultation; Owner: postgres
--

ALTER TABLE consultation.agora_webhook_events ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME consultation.agora_webhook_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: consultation; Type: TABLE; Schema: consultation; Owner: postgres
--

CREATE TABLE consultation.consultation (
    id integer NOT NULL,
    requested_by bigint NOT NULL,
    requested_at timestamp with time zone DEFAULT now() NOT NULL,
    accepted_at timestamp with time zone,
    rejected_at timestamp with time zone,
    rejected_by bigint,
    cancelled_at timestamp with time zone,
    cancelled_reason consultation.cancellation_reason,
    user_joined_at timestamp with time zone,
    expires_at timestamp with time zone,
    profile_id bigint NOT NULL,
    category consultation.consultation_category,
    mode consultation.consultation_mode NOT NULL,
    call_duration_seconds integer DEFAULT 0 NOT NULL,
    rating smallint,
    state consultation.consultation_state DEFAULT 'requested'::consultation.consultation_state NOT NULL,
    version integer DEFAULT 0,
    customer_id bigint NOT NULL,
    guide_id bigint NOT NULL,
    guide_x_auth_id bigint NOT NULL,
    customer_x_auth_id bigint NOT NULL,
    max_call_duration_seconds integer DEFAULT 0,
    completed_by bigint,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    guide_voice_channel_name character varying(1024) DEFAULT ''::character varying NOT NULL,
    guide_video_channel_name character varying(1024) DEFAULT ''::character varying NOT NULL,
    guide_name character varying(1024) DEFAULT ''::character varying NOT NULL,
    order_id bigint DEFAULT 0,
    customer_name character varying(1024) DEFAULT NULL::character varying,
    base_rate_per_minute numeric(10,2) DEFAULT 0.00,
    completed_by_heartbeat boolean DEFAULT false NOT NULL,
    heartbeat_completion_reason text,
    heartbeat_missed_by_user_type text,
    rejection_reason text,
    notification_missed_count integer DEFAULT 0 NOT NULL,
    last_notification_sent_at timestamp with time zone,
    fallback_completion boolean DEFAULT false NOT NULL,
    category_id_for_quick_connect bigint,
    is_quick_connect_request boolean DEFAULT false NOT NULL,
    max_call_duration_minutes bigint,
    cloud_recording_resource_id character varying(255),
    cloud_recording_session_id character varying(255),
    cloud_recording_started_at timestamp without time zone,
    cloud_recording_stopped_at timestamp without time zone,
    promotional boolean DEFAULT false,
    free boolean DEFAULT false,
    effective_base_rate_per_minute numeric(10,2) DEFAULT 0.00,
    offer_reservation_id uuid,
    offer_id uuid,
    offer_applied boolean DEFAULT false NOT NULL,
    offer_snapshot jsonb,
    is_promotional_consultation boolean DEFAULT false NOT NULL,
    is_refundable boolean DEFAULT false NOT NULL,
    is_refunded boolean DEFAULT false NOT NULL,
    forced_by_admin_id bigint,
    CONSTRAINT consultation_heartbeat_missed_by_user_type_check CHECK (((heartbeat_missed_by_user_type = ANY (ARRAY['guide'::text, 'customer'::text, 'both'::text])) OR (heartbeat_missed_by_user_type IS NULL))),
    CONSTRAINT consultation_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE consultation.consultation OWNER TO postgres;

--
-- Name: TABLE consultation; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON TABLE consultation.consultation IS 'Consultation table - wallet_user_id column removed, use guide_id instead';


--
-- Name: COLUMN consultation.base_rate_per_minute; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.base_rate_per_minute IS 'Base rate per minute for the consultation in decimal format';


--
-- Name: COLUMN consultation.completed_by_heartbeat; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.completed_by_heartbeat IS 'Indicates if consultation was completed by heartbeat workflow';


--
-- Name: COLUMN consultation.heartbeat_completion_reason; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.heartbeat_completion_reason IS 'Reason for heartbeat completion (guide_offline, customer_offline, both_clients_offline)';


--
-- Name: COLUMN consultation.heartbeat_missed_by_user_type; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.heartbeat_missed_by_user_type IS 'Which user type missed heartbeat signals (guide, customer, both)';


--
-- Name: COLUMN consultation.rejection_reason; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.rejection_reason IS 'Reason provided when guide rejects consultation';


--
-- Name: COLUMN consultation.notification_missed_count; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.notification_missed_count IS 'Number of notifications missed by guide';


--
-- Name: COLUMN consultation.last_notification_sent_at; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.last_notification_sent_at IS 'Timestamp of last notification sent to guide';


--
-- Name: COLUMN consultation.fallback_completion; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.fallback_completion IS 'True if consultation completed due to fallback logic (timeouts, missed notifications, etc.)';


--
-- Name: COLUMN consultation.cloud_recording_resource_id; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.cloud_recording_resource_id IS 'Agora cloud recording resource ID obtained from acquire API';


--
-- Name: COLUMN consultation.cloud_recording_session_id; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.cloud_recording_session_id IS 'Agora cloud recording session ID obtained from start recording API';


--
-- Name: COLUMN consultation.cloud_recording_started_at; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.cloud_recording_started_at IS 'Timestamp when cloud recording was started';


--
-- Name: COLUMN consultation.cloud_recording_stopped_at; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.cloud_recording_stopped_at IS 'Timestamp when cloud recording was stopped';


--
-- Name: COLUMN consultation.promotional; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.promotional IS 'Indicates if a discount offer was applied to this consultation';


--
-- Name: COLUMN consultation.free; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.free IS 'Indicates if the consultation was completely free (from vouchers like free minutes)';


--
-- Name: COLUMN consultation.effective_base_rate_per_minute; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.effective_base_rate_per_minute IS 'Effective base rate per minute applied to the consultation';


--
-- Name: COLUMN consultation.offer_reservation_id; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.offer_reservation_id IS 'UUID of the offer reservation associated with this consultation';


--
-- Name: COLUMN consultation.offer_id; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.offer_id IS 'UUID of the offer applied to this consultation';


--
-- Name: COLUMN consultation.offer_applied; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.offer_applied IS 'Flag indicating if an offer was applied to this consultation';


--
-- Name: COLUMN consultation.offer_snapshot; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.offer_snapshot IS 'JSONB snapshot of the offer details at the time of application';


--
-- Name: COLUMN consultation.is_promotional_consultation; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.is_promotional_consultation IS 'Indicates if consultation uses voucher offer with free minutes (offer_type=VOUCHER and voucher_free_minutes > 0). Calculated at creation time from offer_snapshot. Immutable throughout consultation lifecycle.';


--
-- Name: COLUMN consultation.is_refundable; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.is_refundable IS 'Marks consultation as eligible for refund (auto-set when guide_message_count=0 for chat, or force-marked by admin)';


--
-- Name: COLUMN consultation.is_refunded; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.is_refunded IS 'Marks consultation as already refunded';


--
-- Name: COLUMN consultation.forced_by_admin_id; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation.forced_by_admin_id IS 'Admin user ID who force-marked this consultation as refundable (NULL if auto-detected)';


--
-- Name: consultation_analytics; Type: VIEW; Schema: consultation; Owner: postgres
--

CREATE VIEW consultation.consultation_analytics AS
 SELECT consultation.state,
    consultation.mode,
    consultation.category,
    count(*) AS total_count,
    count(
        CASE
            WHEN (consultation.created_at >= (now() - '24:00:00'::interval)) THEN 1
            ELSE NULL::integer
        END) AS last_24h_count,
    count(
        CASE
            WHEN (consultation.created_at >= (now() - '7 days'::interval)) THEN 1
            ELSE NULL::integer
        END) AS last_7d_count,
    avg(consultation.call_duration_seconds) AS avg_call_duration_seconds,
    avg(consultation.rating) AS avg_rating
   FROM consultation.consultation
  WHERE (consultation.deleted_at IS NULL)
  GROUP BY consultation.state, consultation.mode, consultation.category;


ALTER VIEW consultation.consultation_analytics OWNER TO postgres;

--
-- Name: consultation_id_seq; Type: SEQUENCE; Schema: consultation; Owner: postgres
--

CREATE SEQUENCE consultation.consultation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE consultation.consultation_id_seq OWNER TO postgres;

--
-- Name: consultation_id_seq; Type: SEQUENCE OWNED BY; Schema: consultation; Owner: postgres
--

ALTER SEQUENCE consultation.consultation_id_seq OWNED BY consultation.consultation.id;


--
-- Name: consultation_quality_metrics; Type: TABLE; Schema: consultation; Owner: postgres
--

CREATE TABLE consultation.consultation_quality_metrics (
    id bigint NOT NULL,
    consultation_id bigint NOT NULL,
    guide_id bigint NOT NULL,
    customer_id bigint NOT NULL,
    is_short_consultation boolean DEFAULT false NOT NULL,
    consultation_duration_seconds integer NOT NULL,
    guide_message_count integer DEFAULT 0 NOT NULL,
    customer_message_count integer DEFAULT 0 NOT NULL,
    total_message_count integer DEFAULT 0 NOT NULL,
    average_guide_response_time_seconds numeric(10,2),
    consultation_mode character varying(50) DEFAULT 'chat'::character varying NOT NULL,
    pair_id character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT check_duration_positive CHECK ((consultation_duration_seconds >= 0)),
    CONSTRAINT check_message_counts CHECK (((guide_message_count >= 0) AND (customer_message_count >= 0) AND (total_message_count >= 0)))
);


ALTER TABLE consultation.consultation_quality_metrics OWNER TO postgres;

--
-- Name: TABLE consultation_quality_metrics; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON TABLE consultation.consultation_quality_metrics IS 'Quality metrics for chat consultations monitoring';


--
-- Name: COLUMN consultation_quality_metrics.is_short_consultation; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation_quality_metrics.is_short_consultation IS 'Flags consultations shorter than 1 minute (60 seconds)';


--
-- Name: COLUMN consultation_quality_metrics.average_guide_response_time_seconds; Type: COMMENT; Schema: consultation; Owner: postgres
--

COMMENT ON COLUMN consultation.consultation_quality_metrics.average_guide_response_time_seconds IS 'Average time guide takes to respond to customer messages';


--
-- Name: consultation_quality_metrics_id_seq; Type: SEQUENCE; Schema: consultation; Owner: postgres
--

CREATE SEQUENCE consultation.consultation_quality_metrics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE consultation.consultation_quality_metrics_id_seq OWNER TO postgres;

--
-- Name: consultation_quality_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: consultation; Owner: postgres
--

ALTER SEQUENCE consultation.consultation_quality_metrics_id_seq OWNED BY consultation.consultation_quality_metrics.id;


--
-- Name: feedback; Type: TABLE; Schema: consultation; Owner: postgres
--

CREATE TABLE consultation.feedback (
    id integer NOT NULL,
    consultation_id bigint NOT NULL,
    customer_id bigint NOT NULL,
    rating smallint NOT NULL,
    feedback text,
    status consultation.feedback_status DEFAULT 'submitted'::consultation.feedback_status NOT NULL,
    report_reason text,
    resolved_at timestamp with time zone,
    resolved_by bigint,
    is_deleted boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    customer_name character varying(255) DEFAULT NULL::character varying,
    reports jsonb DEFAULT '{"guides": [], "customers": []}'::jsonb,
    CONSTRAINT feedback_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE consultation.feedback OWNER TO postgres;

--
-- Name: feedback_comments_by_guide; Type: TABLE; Schema: consultation; Owner: postgres
--

CREATE TABLE consultation.feedback_comments_by_guide (
    id integer NOT NULL,
    feedback_id bigint NOT NULL,
    guide_id bigint NOT NULL,
    comment text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE consultation.feedback_comments_by_guide OWNER TO postgres;

--
-- Name: feedback_comments_by_guide_id_seq; Type: SEQUENCE; Schema: consultation; Owner: postgres
--

CREATE SEQUENCE consultation.feedback_comments_by_guide_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE consultation.feedback_comments_by_guide_id_seq OWNER TO postgres;

--
-- Name: feedback_comments_by_guide_id_seq; Type: SEQUENCE OWNED BY; Schema: consultation; Owner: postgres
--

ALTER SEQUENCE consultation.feedback_comments_by_guide_id_seq OWNED BY consultation.feedback_comments_by_guide.id;


--
-- Name: feedback_id_seq; Type: SEQUENCE; Schema: consultation; Owner: postgres
--

CREATE SEQUENCE consultation.feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE consultation.feedback_id_seq OWNER TO postgres;

--
-- Name: feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: consultation; Owner: postgres
--

ALTER SEQUENCE consultation.feedback_id_seq OWNED BY consultation.feedback.id;


--
-- Name: guide_performance; Type: VIEW; Schema: consultation; Owner: postgres
--

CREATE VIEW consultation.guide_performance AS
 SELECT consultation.guide_id,
    count(*) AS total_consultations,
    count(
        CASE
            WHEN (consultation.state = 'completed'::consultation.consultation_state) THEN 1
            ELSE NULL::integer
        END) AS completed_consultations,
    count(
        CASE
            WHEN (consultation.state = 'cancelled'::consultation.consultation_state) THEN 1
            ELSE NULL::integer
        END) AS cancelled_consultations,
    avg(
        CASE
            WHEN (consultation.rating IS NOT NULL) THEN consultation.rating
            ELSE NULL::smallint
        END) AS avg_rating,
    avg(consultation.call_duration_seconds) AS avg_call_duration,
    count(
        CASE
            WHEN (consultation.created_at >= (now() - '30 days'::interval)) THEN 1
            ELSE NULL::integer
        END) AS consultations_last_30d
   FROM consultation.consultation
  WHERE (consultation.deleted_at IS NULL)
  GROUP BY consultation.guide_id;


ALTER VIEW consultation.guide_performance OWNER TO postgres;

--
-- Name: address; Type: TABLE; Schema: customers; Owner: postgres
--

CREATE TABLE customers.address (
    address_id bigint NOT NULL,
    street character varying(255),
    city character varying(100),
    pincode character varying(20),
    state character varying(100),
    country character varying(100),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    version bigint DEFAULT 1,
    deleted_at timestamp with time zone
);


ALTER TABLE customers.address OWNER TO postgres;

--
-- Name: address_address_id_seq; Type: SEQUENCE; Schema: customers; Owner: postgres
--

CREATE SEQUENCE customers.address_address_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE customers.address_address_id_seq OWNER TO postgres;

--
-- Name: address_address_id_seq; Type: SEQUENCE OWNED BY; Schema: customers; Owner: postgres
--

ALTER SEQUENCE customers.address_address_id_seq OWNED BY customers.address.address_id;


--
-- Name: customer; Type: TABLE; Schema: customers; Owner: postgres
--

CREATE TABLE customers.customer (
    customer_id bigint NOT NULL,
    phone_number text,
    country_code text,
    wallet_user_id bigint,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    version bigint,
    x_auth_id bigint,
    deleted_at timestamp with time zone
);


ALTER TABLE customers.customer OWNER TO postgres;

--
-- Name: TABLE customer; Type: COMMENT; Schema: customers; Owner: postgres
--

COMMENT ON TABLE customers.customer IS 'Customer table - wallet_id column removed, wallet operations handled through wallet service';


--
-- Name: customer_address; Type: TABLE; Schema: customers; Owner: postgres
--

CREATE TABLE customers.customer_address (
    customer_address_id bigint NOT NULL,
    customer_id bigint NOT NULL,
    address_id bigint NOT NULL,
    is_primary boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    version bigint DEFAULT 1,
    deleted_at timestamp with time zone
);


ALTER TABLE customers.customer_address OWNER TO postgres;

--
-- Name: customer_address_customer_address_id_seq; Type: SEQUENCE; Schema: customers; Owner: postgres
--

CREATE SEQUENCE customers.customer_address_customer_address_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE customers.customer_address_customer_address_id_seq OWNER TO postgres;

--
-- Name: customer_address_customer_address_id_seq; Type: SEQUENCE OWNED BY; Schema: customers; Owner: postgres
--

ALTER SEQUENCE customers.customer_address_customer_address_id_seq OWNED BY customers.customer_address.customer_address_id;


--
-- Name: customer_customer_id_seq; Type: SEQUENCE; Schema: customers; Owner: postgres
--

CREATE SEQUENCE customers.customer_customer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE customers.customer_customer_id_seq OWNER TO postgres;

--
-- Name: customer_customer_id_seq; Type: SEQUENCE OWNED BY; Schema: customers; Owner: postgres
--

ALTER SEQUENCE customers.customer_customer_id_seq OWNED BY customers.customer.customer_id;


--
-- Name: customer_profile; Type: TABLE; Schema: customers; Owner: postgres
--

CREATE TABLE customers.customer_profile (
    profile_id bigint NOT NULL,
    customer_id bigint NOT NULL,
    name character varying(100),
    dob date,
    tob character varying(20),
    birth_city character varying(100),
    birth_country character varying(100),
    preferred_language character varying(10),
    zodiac_sign character varying(20),
    pob_lat numeric(10,8),
    pob_long numeric(11,8),
    is_primary boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    version bigint DEFAULT 1,
    left_hand_image_url text,
    right_hand_image_url text,
    left_hand_image_hash character varying(64),
    right_hand_image_hash character varying(64),
    profile_image_url text,
    profile_image_index integer,
    deleted_at timestamp with time zone,
    gender character varying(20)
);


ALTER TABLE customers.customer_profile OWNER TO postgres;

--
-- Name: COLUMN customer_profile.gender; Type: COMMENT; Schema: customers; Owner: postgres
--

COMMENT ON COLUMN customers.customer_profile.gender IS 'Customer gender preference (e.g., Male, Female, Other, Prefer not to say). Optional field.';


--
-- Name: customer_profile_profile_id_seq; Type: SEQUENCE; Schema: customers; Owner: postgres
--

CREATE SEQUENCE customers.customer_profile_profile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE customers.customer_profile_profile_id_seq OWNER TO postgres;

--
-- Name: customer_profile_profile_id_seq; Type: SEQUENCE OWNED BY; Schema: customers; Owner: postgres
--

ALTER SEQUENCE customers.customer_profile_profile_id_seq OWNED BY customers.customer_profile.profile_id;


--
-- Name: addresses; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.addresses (
    id bigint NOT NULL,
    guide_id bigint,
    label character varying(255) NOT NULL,
    landmark character varying(255),
    line1 character varying(255) NOT NULL,
    line2 character varying(255),
    city character varying(100) NOT NULL,
    state character varying(100) NOT NULL,
    state_code character varying(10),
    pincode character varying(20) NOT NULL,
    country character varying(100) NOT NULL,
    country_code character varying(10),
    address_tag character varying(50),
    latitude numeric,
    longitude numeric,
    is_default boolean DEFAULT false NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.addresses OWNER TO postgres;

--
-- Name: addresses_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.addresses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.addresses_id_seq OWNER TO postgres;

--
-- Name: addresses_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.addresses_id_seq OWNED BY guide.addresses.id;


--
-- Name: agreement; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.agreement (
    id bigint NOT NULL,
    guide_id bigint,
    url text NOT NULL,
    status guide.agreement_status_enum DEFAULT 'generated'::guide.agreement_status_enum NOT NULL,
    sent_by integer,
    revoked_at timestamp with time zone,
    revoked_by integer,
    webhook_data jsonb DEFAULT '{}'::jsonb,
    is_signed boolean DEFAULT false,
    is_deleted boolean DEFAULT false,
    deleted_by bigint,
    signed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.agreement OWNER TO postgres;

--
-- Name: agreement_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.agreement_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.agreement_id_seq OWNER TO postgres;

--
-- Name: agreement_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.agreement_id_seq OWNED BY guide.agreement.id;


--
-- Name: bank_account; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.bank_account (
    id bigint NOT NULL,
    guide_id bigint,
    account_holder_name character varying(100) NOT NULL,
    account_number character varying(100) NOT NULL,
    bank_name character varying(100) NOT NULL,
    branch_name character varying(100),
    ifsc_code character varying(16) NOT NULL,
    is_default boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.bank_account OWNER TO postgres;

--
-- Name: bank_account_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.bank_account_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.bank_account_id_seq OWNER TO postgres;

--
-- Name: bank_account_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.bank_account_id_seq OWNED BY guide.bank_account.id;


--
-- Name: guide_languages; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.guide_languages (
    guide_id bigint NOT NULL,
    language_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.guide_languages OWNER TO postgres;

--
-- Name: guide_profile; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.guide_profile (
    id bigint NOT NULL,
    x_auth_id bigint NOT NULL,
    full_name character varying(50) NOT NULL,
    phone_number character varying(15) NOT NULL,
    email character varying(255) NOT NULL,
    date_of_birth date,
    profile_picture_url text,
    bio text,
    onboarding_state guide.onboarding_state_enum DEFAULT 'REGISTRATION_PENDING'::guide.onboarding_state_enum NOT NULL,
    chat_enabled boolean DEFAULT false NOT NULL,
    voice_enabled boolean DEFAULT false NOT NULL,
    video_enabled boolean DEFAULT false NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    years_of_experience integer,
    referral_code character varying(64),
    referrer_code character varying(64),
    referral_count integer DEFAULT 0 NOT NULL,
    properties jsonb DEFAULT jsonb_build_object('is_celebrity', false) NOT NULL,
    voice_channel_name character varying(50),
    video_channel_name character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    wallet_id bigint,
    number_of_pending_consultation_requests bigint,
    availability_state character varying(32) DEFAULT 'OFFLINE'::character varying NOT NULL,
    is_deleted boolean DEFAULT false,
    guide_stats jsonb DEFAULT jsonb_build_object('total_number_of_completed_consultations', 0, 'total_number_of_chat_consultations', 0, 'total_number_of_voice_consultations', 0, 'total_number_of_video_consultations', 0, 'total_chat_minutes', 0, 'total_voice_minutes', 0, 'total_video_minutes', 0, 'total_consultation_minutes', 0, 'total_quick_connect_consultations', 0, 'total_quick_connect_consultation_minutes', 0, 'rating', 0.0, 'total_number_of_reviews', 0, 'review_breakdown', jsonb_build_object('number_of_one_star_reviews', 0, 'number_of_two_star_reviews', 0, 'number_of_three_star_reviews', 0, 'number_of_four_star_reviews', 0, 'number_of_five_star_reviews', 0), 'average_consultation_length', 0, 'average_consultation_length_chat', 0, 'average_consultation_length_voice', 0, 'average_consultation_length_video', 0) NOT NULL,
    ranking_score numeric DEFAULT 0 NOT NULL,
    tier character varying(20) DEFAULT 'basic'::character varying NOT NULL,
    CONSTRAINT chk_guide_stats_structure CHECK (((jsonb_typeof(guide_stats) = 'object'::text) AND (jsonb_typeof((guide_stats -> 'total_number_of_completed_consultations'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'total_number_of_chat_consultations'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'total_number_of_voice_consultations'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'total_number_of_video_consultations'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'total_chat_minutes'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'total_voice_minutes'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'total_video_minutes'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'total_consultation_minutes'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'total_quick_connect_consultations'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'total_quick_connect_consultation_minutes'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'rating'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'total_number_of_reviews'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'review_breakdown'::text)) = 'object'::text) AND (jsonb_typeof((guide_stats -> 'average_consultation_length'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'average_consultation_length_chat'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'average_consultation_length_voice'::text)) = 'number'::text) AND (jsonb_typeof((guide_stats -> 'average_consultation_length_video'::text)) = 'number'::text) AND (jsonb_typeof(((guide_stats -> 'review_breakdown'::text) -> 'number_of_one_star_reviews'::text)) = 'number'::text) AND (jsonb_typeof(((guide_stats -> 'review_breakdown'::text) -> 'number_of_two_star_reviews'::text)) = 'number'::text) AND (jsonb_typeof(((guide_stats -> 'review_breakdown'::text) -> 'number_of_three_star_reviews'::text)) = 'number'::text) AND (jsonb_typeof(((guide_stats -> 'review_breakdown'::text) -> 'number_of_four_star_reviews'::text)) = 'number'::text) AND (jsonb_typeof(((guide_stats -> 'review_breakdown'::text) -> 'number_of_five_star_reviews'::text)) = 'number'::text))),
    CONSTRAINT chk_is_deleted_consistency CHECK ((((deleted_at IS NULL) AND (is_deleted = false)) OR ((deleted_at IS NOT NULL) AND (is_deleted = true)))),
    CONSTRAINT chk_phone_format CHECK (((phone_number)::text ~ '^\+?\d{10,14}$'::text)),
    CONSTRAINT chk_properties_is_object CHECK ((jsonb_typeof(properties) = 'object'::text)),
    CONSTRAINT chk_properties_whitelist CHECK (((jsonb_typeof(properties) = 'object'::text) AND (properties ? 'is_celebrity'::text) AND (jsonb_typeof((properties -> 'is_celebrity'::text)) = 'boolean'::text) AND ((NOT (properties ? 'is_test_guide'::text)) OR (jsonb_typeof((properties -> 'is_test_guide'::text)) = 'boolean'::text)) AND ((NOT (properties ? 'tier'::text)) OR ((jsonb_typeof((properties -> 'tier'::text)) = 'string'::text) AND ((properties ->> 'tier'::text) = ANY (ARRAY['basic'::text, 'standard'::text, 'premium'::text, 'elite'::text])))))),
    CONSTRAINT chk_tier_values CHECK (((tier)::text = ANY ((ARRAY['basic'::character varying, 'standard'::character varying, 'premium'::character varying, 'elite'::character varying])::text[])))
);


ALTER TABLE guide.guide_profile OWNER TO postgres;

--
-- Name: COLUMN guide_profile.is_deleted; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON COLUMN guide.guide_profile.is_deleted IS 'Soft delete flag, true when account is deleted';


--
-- Name: COLUMN guide_profile.guide_stats; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON COLUMN guide.guide_profile.guide_stats IS 'JSONB column storing comprehensive guide statistics including consultation counts, duration metrics, ratings, review breakdowns, and quick connect metrics';


--
-- Name: COLUMN guide_profile.ranking_score; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON COLUMN guide.guide_profile.ranking_score IS 'Manual ranking score for guide prioritization in listings. Higher scores appear first. Default is 0.';


--
-- Name: COLUMN guide_profile.tier; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON COLUMN guide.guide_profile.tier IS 'Guide tier level: basic (default), standard, premium, or elite';


--
-- Name: CONSTRAINT chk_properties_whitelist ON guide_profile; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON CONSTRAINT chk_properties_whitelist ON guide.guide_profile IS 'Ensures properties JSONB contains valid is_celebrity, is_test_guide boolean flags, and optional tier enum value';


--
-- Name: guide_profile_audit; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.guide_profile_audit (
    id bigint NOT NULL,
    guide_id bigint NOT NULL,
    from_state guide.onboarding_state_enum,
    to_state guide.onboarding_state_enum,
    changed_by integer,
    diff jsonb DEFAULT '{}'::jsonb,
    changed_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.guide_profile_audit OWNER TO postgres;

--
-- Name: COLUMN guide_profile_audit.deleted_at; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON COLUMN guide.guide_profile_audit.deleted_at IS 'Soft delete timestamp for audit records';


--
-- Name: guide_profile_audit_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.guide_profile_audit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.guide_profile_audit_id_seq OWNER TO postgres;

--
-- Name: guide_profile_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.guide_profile_audit_id_seq OWNED BY guide.guide_profile_audit.id;


--
-- Name: guide_profile_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.guide_profile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.guide_profile_id_seq OWNER TO postgres;

--
-- Name: guide_profile_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.guide_profile_id_seq OWNED BY guide.guide_profile.id;


--
-- Name: guide_skills; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.guide_skills (
    guide_id bigint NOT NULL,
    skill_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.guide_skills OWNER TO postgres;

--
-- Name: kyc_document; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.kyc_document (
    id bigint NOT NULL,
    guide_id bigint,
    document_type guide.document_type_enum NOT NULL,
    mime_type text NOT NULL,
    url text NOT NULL,
    tags text[] DEFAULT '{}'::text[],
    tag_first text GENERATED ALWAYS AS (tags[1]) STORED,
    document_sha256 character varying(64),
    metadata jsonb DEFAULT '{}'::jsonb,
    s3_bucket_url text,
    document_blob bytea,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.kyc_document OWNER TO postgres;

--
-- Name: kyc_document_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.kyc_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.kyc_document_id_seq OWNER TO postgres;

--
-- Name: kyc_document_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.kyc_document_id_seq OWNED BY guide.kyc_document.id;


--
-- Name: languages; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.languages (
    id bigint NOT NULL,
    name character varying(64) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.languages OWNER TO postgres;

--
-- Name: languages_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.languages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.languages_id_seq OWNER TO postgres;

--
-- Name: languages_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.languages_id_seq OWNED BY guide.languages.id;


--
-- Name: media; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.media (
    id bigint NOT NULL,
    guide_id bigint,
    media_type character varying(20) NOT NULL,
    original_filename character varying(255) NOT NULL,
    cdn_url text NOT NULL,
    width integer,
    height integer,
    image_blob bytea,
    document_sha256 character varying(64),
    processed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.media OWNER TO postgres;

--
-- Name: media_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.media_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.media_id_seq OWNER TO postgres;

--
-- Name: media_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.media_id_seq OWNED BY guide.media.id;


--
-- Name: saved_messages; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.saved_messages (
    id bigint NOT NULL,
    guide_id bigint NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT chk_content_not_empty CHECK ((length(TRIM(BOTH FROM content)) > 0)),
    CONSTRAINT chk_title_not_empty CHECK ((length(TRIM(BOTH FROM title)) > 0))
);


ALTER TABLE guide.saved_messages OWNER TO postgres;

--
-- Name: TABLE saved_messages; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON TABLE guide.saved_messages IS 'Stores saved messages for guides. Supports 1->N relationship where each guide can have multiple saved messages. Includes soft delete support.';


--
-- Name: COLUMN saved_messages.guide_id; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON COLUMN guide.saved_messages.guide_id IS 'Foreign key reference to guide_profile. Each message belongs to one guide.';


--
-- Name: COLUMN saved_messages.title; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON COLUMN guide.saved_messages.title IS 'Title of the saved message. Searchable and must not be empty.';


--
-- Name: COLUMN saved_messages.content; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON COLUMN guide.saved_messages.content IS 'Content of the saved message. Searchable and must not be empty.';


--
-- Name: COLUMN saved_messages.deleted_at; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON COLUMN guide.saved_messages.deleted_at IS 'Timestamp for soft delete. NULL means the message is active.';


--
-- Name: saved_messages_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.saved_messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.saved_messages_id_seq OWNER TO postgres;

--
-- Name: saved_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.saved_messages_id_seq OWNED BY guide.saved_messages.id;


--
-- Name: skills; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.skills (
    id bigint NOT NULL,
    name character varying(64) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.skills OWNER TO postgres;

--
-- Name: skills_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.skills_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.skills_id_seq OWNER TO postgres;

--
-- Name: skills_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.skills_id_seq OWNED BY guide.skills.id;


--
-- Name: verification; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.verification (
    id bigint NOT NULL,
    guide_id bigint NOT NULL,
    target_type guide.verification_target_enum NOT NULL,
    kyc_document_id bigint,
    bank_account_id bigint,
    agreement_id bigint,
    status guide.verification_status_enum DEFAULT 'uploaded'::guide.verification_status_enum NOT NULL,
    verified_by integer,
    rejected_by integer,
    rejection_reason text,
    verified_at timestamp with time zone,
    tags text[] DEFAULT '{}'::text[],
    is_manual boolean DEFAULT false NOT NULL,
    manual_verified_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT verification_check CHECK ((((target_type = 'KYC_DOCUMENT'::guide.verification_target_enum) AND (kyc_document_id IS NOT NULL)) OR ((target_type = 'BANK_ACCOUNT'::guide.verification_target_enum) AND (bank_account_id IS NOT NULL)) OR ((target_type = 'AGREEMENT'::guide.verification_target_enum) AND (agreement_id IS NOT NULL)))),
    CONSTRAINT verification_tags_check CHECK ((array_length(tags, 1) <= 20))
);


ALTER TABLE guide.verification OWNER TO postgres;

--
-- Name: verification_audit_log; Type: TABLE; Schema: guide; Owner: postgres
--

CREATE TABLE guide.verification_audit_log (
    id bigint NOT NULL,
    guide_id bigint NOT NULL,
    document_id bigint NOT NULL,
    admin_id bigint NOT NULL,
    action character varying(16) NOT NULL,
    reason text,
    target_type guide.verification_target_enum NOT NULL,
    status guide.verification_status_enum NOT NULL,
    kyc_document_id bigint,
    bank_account_id bigint,
    agreement_id bigint,
    metadata jsonb DEFAULT '{}'::jsonb,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE guide.verification_audit_log OWNER TO postgres;

--
-- Name: COLUMN verification_audit_log.deleted_at; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON COLUMN guide.verification_audit_log.deleted_at IS 'Soft delete timestamp for verification audit records';


--
-- Name: verification_audit_log_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.verification_audit_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.verification_audit_log_id_seq OWNER TO postgres;

--
-- Name: verification_audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.verification_audit_log_id_seq OWNED BY guide.verification_audit_log.id;


--
-- Name: verification_id_seq; Type: SEQUENCE; Schema: guide; Owner: postgres
--

CREATE SEQUENCE guide.verification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guide.verification_id_seq OWNER TO postgres;

--
-- Name: verification_id_seq; Type: SEQUENCE OWNED BY; Schema: guide; Owner: postgres
--

ALTER SEQUENCE guide.verification_id_seq OWNED BY guide.verification.id;


--
-- Name: vw_guide_current_verifications; Type: VIEW; Schema: guide; Owner: postgres
--

CREATE VIEW guide.vw_guide_current_verifications AS
 SELECT DISTINCT ON (verification.guide_id, verification.target_type) verification.guide_id,
    verification.target_type,
    verification.status,
    verification.verified_at,
    verification.updated_at
   FROM guide.verification
  WHERE (verification.deleted_at IS NULL)
  ORDER BY verification.guide_id, verification.target_type, verification.verified_at DESC NULLS LAST, verification.id DESC;


ALTER VIEW guide.vw_guide_current_verifications OWNER TO postgres;

--
-- Name: leads; Type: TABLE; Schema: marketing; Owner: postgres
--

CREATE TABLE marketing.leads (
    id bigint NOT NULL,
    phone character varying(15) NOT NULL,
    name character varying(100),
    source character varying(50),
    utm_source character varying(100),
    utm_medium character varying(100),
    utm_campaign character varying(255),
    status character varying(20) DEFAULT 'new'::character varying,
    info jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE marketing.leads OWNER TO postgres;

--
-- Name: leads_id_seq; Type: SEQUENCE; Schema: marketing; Owner: postgres
--

CREATE SEQUENCE marketing.leads_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE marketing.leads_id_seq OWNER TO postgres;

--
-- Name: leads_id_seq; Type: SEQUENCE OWNED BY; Schema: marketing; Owner: postgres
--

ALTER SEQUENCE marketing.leads_id_seq OWNED BY marketing.leads.id;


--
-- Name: messages; Type: TABLE; Schema: marketing; Owner: postgres
--

CREATE TABLE marketing.messages (
    type character varying(50) NOT NULL,
    key character varying(50) NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE marketing.messages OWNER TO postgres;

--
-- Name: client_events; Type: TABLE; Schema: notifications; Owner: postgres
--

CREATE TABLE notifications.client_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_id text NOT NULL,
    event_type text NOT NULL,
    user_id text NOT NULL,
    device_id text NOT NULL,
    platform text NOT NULL,
    app_version text NOT NULL,
    priority text NOT NULL,
    payload jsonb,
    "timestamp" timestamp with time zone NOT NULL,
    ip_address text,
    user_agent text,
    session_id text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE notifications.client_events OWNER TO postgres;

--
-- Name: delivery_attempts; Type: TABLE; Schema: notifications; Owner: postgres
--

CREATE TABLE notifications.delivery_attempts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_id uuid NOT NULL,
    channel text NOT NULL,
    status text NOT NULL,
    attempt_number bigint DEFAULT 1 NOT NULL,
    device_token text,
    recipient text,
    error_message text,
    response_data jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    delivered_at timestamp with time zone,
    next_retry_at timestamp with time zone
);


ALTER TABLE notifications.delivery_attempts OWNER TO postgres;

--
-- Name: escalation_rules; Type: TABLE; Schema: notifications; Owner: postgres
--

CREATE TABLE notifications.escalation_rules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type text NOT NULL,
    priority text NOT NULL,
    primary_channel text NOT NULL,
    secondary_channel text,
    tertiary_channel text,
    escalation_delay bigint DEFAULT 300 NOT NULL,
    max_attempts bigint DEFAULT 3 NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE notifications.escalation_rules OWNER TO postgres;

--
-- Name: notifications; Type: TABLE; Schema: notifications; Owner: postgres
--

CREATE TABLE notifications.notifications (
    event_id uuid DEFAULT gen_random_uuid() NOT NULL,
    auth_user_id text NOT NULL,
    target_type text,
    event_type text NOT NULL,
    channel text NOT NULL,
    priority text NOT NULL,
    payload jsonb,
    is_read boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    scheduled_at timestamp with time zone,
    delivered_at timestamp with time zone,
    read_at timestamp with time zone
);


ALTER TABLE notifications.notifications OWNER TO postgres;

--
-- Name: offer_definitions; Type: TABLE; Schema: offers; Owner: postgres
--

CREATE TABLE offers.offer_definitions (
    offer_id uuid DEFAULT gen_random_uuid() NOT NULL,
    offer_name text NOT NULL,
    description text,
    offer_type text NOT NULL,
    offer_category text NOT NULL,
    bonus_percentage numeric(10,2) DEFAULT 0,
    bonus_fixed_amount numeric(10,2) DEFAULT 0,
    min_recharge_amount numeric(10,2) DEFAULT 0,
    max_recharge_amount numeric(10,2) DEFAULT 0,
    target_user_types text[],
    service_type text,
    time_constraints jsonb,
    consultation_modes text[],
    usage_limit_per_user bigint DEFAULT 0,
    valid_from timestamp with time zone NOT NULL,
    valid_to timestamp with time zone NOT NULL,
    is_active boolean DEFAULT true,
    trigger_type character varying(50),
    voucher_subtype character varying(50),
    cta_url character varying(512),
    cta_text character varying(100) DEFAULT 'Apply Offer'::character varying,
    max_cashback_amount numeric(10,2),
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    applicable_consultants bigint[],
    all_consultant_applicable boolean DEFAULT false NOT NULL,
    target_guide_tiers text[],
    free_minutes bigint
);


ALTER TABLE offers.offer_definitions OWNER TO postgres;

--
-- Name: TABLE offer_definitions; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON TABLE offers.offer_definitions IS 'Core offer definitions with configuration and targeting rules';


--
-- Name: COLUMN offer_definitions.target_user_types; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_definitions.target_user_types IS 'Array of user types this offer applies to: first_time, regular, premium, vip';


--
-- Name: COLUMN offer_definitions.trigger_type; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_definitions.trigger_type IS 'Event that triggers offer: ON_RECHARGE, ON_CONSULTATION, ON_REGISTRATION, MANUAL';


--
-- Name: COLUMN offer_definitions.voucher_subtype; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_definitions.voucher_subtype IS 'For voucher-type offers: FREE_MINUTES (consultation) or FREE_CREDIT (wallet deposit)';


--
-- Name: COLUMN offer_definitions.cta_url; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_definitions.cta_url IS 'Call-to-action URL for offer card (e.g., /recharge, /consultants)';


--
-- Name: COLUMN offer_definitions.cta_text; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_definitions.cta_text IS 'CTA button text (e.g., Recharge Now, Book Session)';


--
-- Name: COLUMN offer_definitions.free_minutes; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_definitions.free_minutes IS 'Free minutes for FREE_MINUTES voucher type (separate from bonus_fixed_amount which is for FREE_CREDIT)';


--
-- Name: offer_reservations; Type: TABLE; Schema: offers; Owner: postgres
--

CREATE TABLE offers.offer_reservations (
    reservation_id uuid DEFAULT gen_random_uuid() NOT NULL,
    offer_id uuid NOT NULL,
    user_id bigint NOT NULL,
    payment_order_id bigint,
    reservation_status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    original_amount numeric(10,2) NOT NULL,
    bonus_amount numeric(10,2) NOT NULL,
    final_amount numeric(10,2) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    consumed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone,
    voucher_minutes bigint,
    voucher_free_cash numeric(10,2),
    wallet_order_id bigint,
    source character varying(50),
    reason text,
    consultation_id bigint
);


ALTER TABLE offers.offer_reservations OWNER TO postgres;

--
-- Name: TABLE offer_reservations; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON TABLE offers.offer_reservations IS 'Offer reservations before consumption';


--
-- Name: COLUMN offer_reservations.payment_order_id; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_reservations.payment_order_id IS 'Recharge transaction order ID for WALLET_RECHARGE/COMBO offers';


--
-- Name: COLUMN offer_reservations.reservation_status; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_reservations.reservation_status IS 'Current status: ACTIVE, CONSUMED, CANCELLED, EXPIRED';


--
-- Name: COLUMN offer_reservations.expires_at; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_reservations.expires_at IS 'Expiration time for the reservation';


--
-- Name: COLUMN offer_reservations.wallet_order_id; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_reservations.wallet_order_id IS 'Consultation billing order ID for VOUCHER/CONSULTANT_PRICING offers';


--
-- Name: COLUMN offer_reservations.source; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_reservations.source IS 'Source of the reservation (e.g., "refund_workflow", "manual", "payment")';


--
-- Name: COLUMN offer_reservations.reason; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_reservations.reason IS 'Reason for the reservation (e.g., "Refund for consultation #12345")';


--
-- Name: COLUMN offer_reservations.consultation_id; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_reservations.consultation_id IS 'Consultation ID if this reservation was created for a refund';


--
-- Name: user_behavior_metrics; Type: TABLE; Schema: offers; Owner: postgres
--

CREATE TABLE offers.user_behavior_metrics (
    user_id bigint NOT NULL,
    registration_source character varying(50) DEFAULT 'ORGANIC'::character varying,
    is_first_time_user boolean DEFAULT true,
    user_type character varying(20),
    first_recharge_at timestamp with time zone,
    total_consultations integer DEFAULT 0,
    total_spent numeric(15,2) DEFAULT 0.00,
    last_activity_at timestamp with time zone,
    user_segment character varying(20) DEFAULT 'NEW'::character varying,
    total_offers_used integer DEFAULT 0,
    last_offer_used_at timestamp with time zone,
    average_consultation_duration integer DEFAULT 0,
    preferred_service_type character varying(20) DEFAULT NULL::character varying,
    last_consultation_at timestamp with time zone,
    total_quick_connect_consultations integer DEFAULT 0,
    offers_used_till_date text[],
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone
);


ALTER TABLE offers.user_behavior_metrics OWNER TO postgres;

--
-- Name: TABLE user_behavior_metrics; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON TABLE offers.user_behavior_metrics IS 'User behavior metrics and segmentation data';


--
-- Name: active_reservations_with_user_info; Type: VIEW; Schema: offers; Owner: postgres
--

CREATE VIEW offers.active_reservations_with_user_info AS
 SELECT r.reservation_id,
    r.offer_id,
    r.user_id,
    r.payment_order_id,
    r.reservation_status,
    r.original_amount,
    r.bonus_amount,
    r.final_amount,
    r.expires_at,
    r.consumed_at,
    r.created_at,
    r.updated_at,
    od.offer_name,
    od.bonus_percentage,
    od.target_user_types,
    ubm.user_segment,
    ubm.registration_source
   FROM ((offers.offer_reservations r
     JOIN offers.offer_definitions od ON ((r.offer_id = od.offer_id)))
     LEFT JOIN offers.user_behavior_metrics ubm ON ((r.user_id = ubm.user_id)))
  WHERE (((r.reservation_status)::text = 'ACTIVE'::text) AND (r.expires_at > now()) AND (r.deleted_at IS NULL));


ALTER VIEW offers.active_reservations_with_user_info OWNER TO postgres;

--
-- Name: VIEW active_reservations_with_user_info; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON VIEW offers.active_reservations_with_user_info IS 'View of active reservations with user and offer details';


--
-- Name: consultant_rates; Type: TABLE; Schema: offers; Owner: postgres
--

CREATE TABLE offers.consultant_rates (
    rate_id uuid DEFAULT gen_random_uuid() NOT NULL,
    consultant_id bigint NOT NULL,
    service_type character varying(20) NOT NULL,
    base_rate numeric(10,2) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    valid_from timestamp with time zone,
    valid_to timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone
);


ALTER TABLE offers.consultant_rates OWNER TO postgres;

--
-- Name: TABLE consultant_rates; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON TABLE offers.consultant_rates IS 'Simplified consultant base rates - time variations handled by offers system';


--
-- Name: offer_consumptions; Type: TABLE; Schema: offers; Owner: postgres
--

CREATE TABLE offers.offer_consumptions (
    consumption_id uuid DEFAULT gen_random_uuid() NOT NULL,
    reservation_id uuid,
    offer_id uuid NOT NULL,
    user_id bigint NOT NULL,
    payment_order_id bigint,
    consumption_status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    original_amount numeric(10,2) NOT NULL,
    bonus_amount numeric(10,2) NOT NULL,
    final_amount numeric(10,2) NOT NULL,
    wallet_transaction_id character varying(255),
    voucher_instance_id uuid,
    consumed_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone,
    voucher_minutes bigint,
    voucher_free_cash numeric(10,2),
    wallet_order_id bigint
);


ALTER TABLE offers.offer_consumptions OWNER TO postgres;

--
-- Name: TABLE offer_consumptions; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON TABLE offers.offer_consumptions IS 'Ledger of offer consumption records';


--
-- Name: COLUMN offer_consumptions.payment_order_id; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_consumptions.payment_order_id IS 'Recharge transaction order ID for WALLET_RECHARGE/COMBO offers';


--
-- Name: COLUMN offer_consumptions.consumption_status; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_consumptions.consumption_status IS 'Status: PENDING, COMPLETED, FAILED, REFUNDED';


--
-- Name: COLUMN offer_consumptions.wallet_transaction_id; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_consumptions.wallet_transaction_id IS 'Reference to wallet transaction for bonus credit';


--
-- Name: COLUMN offer_consumptions.wallet_order_id; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.offer_consumptions.wallet_order_id IS 'Consultation billing order ID for VOUCHER/CONSULTANT_PRICING offers';


--
-- Name: consumption_analytics_view; Type: VIEW; Schema: offers; Owner: postgres
--

CREATE VIEW offers.consumption_analytics_view AS
 SELECT c.consumption_id,
    c.reservation_id,
    c.offer_id,
    c.user_id,
    c.consumption_status,
    c.original_amount,
    c.bonus_amount,
    c.final_amount,
    c.consumed_at,
    c.completed_at,
    od.offer_name,
    od.offer_type,
    od.offer_category,
    od.target_user_types,
    ubm.user_segment,
    ubm.registration_source
   FROM ((offers.offer_consumptions c
     JOIN offers.offer_definitions od ON ((c.offer_id = od.offer_id)))
     LEFT JOIN offers.user_behavior_metrics ubm ON ((c.user_id = ubm.user_id)))
  WHERE (c.deleted_at IS NULL);


ALTER VIEW offers.consumption_analytics_view OWNER TO postgres;

--
-- Name: offer_campaigns; Type: TABLE; Schema: offers; Owner: postgres
--

CREATE TABLE offers.offer_campaigns (
    campaign_id uuid DEFAULT gen_random_uuid() NOT NULL,
    campaign_name character varying(255) NOT NULL,
    description text,
    offer_id uuid NOT NULL,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    target_user_segment character varying(100),
    user_count_limit integer DEFAULT 0,
    status character varying(20) DEFAULT 'active'::character varying NOT NULL,
    distributed_count integer DEFAULT 0,
    created_by bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone,
    CONSTRAINT offer_campaigns_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'paused'::character varying, 'completed'::character varying])::text[]))),
    CONSTRAINT offer_campaigns_user_count_limit_check CHECK ((user_count_limit >= 0))
);


ALTER TABLE offers.offer_campaigns OWNER TO postgres;

--
-- Name: TABLE offer_campaigns; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON TABLE offers.offer_campaigns IS 'Generic campaigns for distributing offer instances';


--
-- Name: offer_usage_view; Type: VIEW; Schema: offers; Owner: postgres
--

CREATE VIEW offers.offer_usage_view AS
 SELECT c.consumption_id AS usage_id,
    c.offer_id,
    c.user_id,
    c.original_amount AS recharge_amount,
    c.bonus_amount,
    c.consumed_at AS used_at,
    c.consumption_status,
    c.deleted_at,
    c.final_amount
   FROM offers.offer_consumptions c;


ALTER VIEW offers.offer_usage_view OWNER TO postgres;

--
-- Name: user_milestone_progress; Type: TABLE; Schema: offers; Owner: postgres
--

CREATE TABLE offers.user_milestone_progress (
    progress_id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id bigint NOT NULL,
    offer_id uuid NOT NULL,
    milestone_reached boolean DEFAULT false,
    trigger_event character varying(50),
    trigger_count integer,
    trigger_amount numeric(10,2),
    triggered_at timestamp with time zone,
    voucher_distributed boolean DEFAULT false,
    voucher_instance_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone
);


ALTER TABLE offers.user_milestone_progress OWNER TO postgres;

--
-- Name: TABLE user_milestone_progress; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON TABLE offers.user_milestone_progress IS 'Tracks user progress towards milestone-based offers and rewards distribution';


--
-- Name: user_segmentation_analytics; Type: VIEW; Schema: offers; Owner: postgres
--

CREATE VIEW offers.user_segmentation_analytics AS
 SELECT user_behavior_metrics.user_segment,
    count(*) AS user_count,
    count(
        CASE
            WHEN (user_behavior_metrics.is_first_time_user = true) THEN 1
            ELSE NULL::integer
        END) AS first_time_users,
    count(
        CASE
            WHEN (user_behavior_metrics.first_recharge_at IS NOT NULL) THEN 1
            ELSE NULL::integer
        END) AS recharged_users,
    avg(user_behavior_metrics.total_consultations) AS avg_consultations,
    avg(user_behavior_metrics.total_spent) AS avg_spent,
    avg(user_behavior_metrics.total_offers_used) AS avg_offers_used,
    count(
        CASE
            WHEN (user_behavior_metrics.last_activity_at >= (now() - '30 days'::interval)) THEN 1
            ELSE NULL::integer
        END) AS active_last_30_days,
    count(
        CASE
            WHEN (user_behavior_metrics.last_activity_at >= (now() - '7 days'::interval)) THEN 1
            ELSE NULL::integer
        END) AS active_last_7_days
   FROM offers.user_behavior_metrics
  WHERE (user_behavior_metrics.deleted_at IS NULL)
  GROUP BY user_behavior_metrics.user_segment
  ORDER BY user_behavior_metrics.user_segment;


ALTER VIEW offers.user_segmentation_analytics OWNER TO postgres;

--
-- Name: VIEW user_segmentation_analytics; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON VIEW offers.user_segmentation_analytics IS 'Analytics view for user segmentation data';


--
-- Name: user_segments; Type: TABLE; Schema: offers; Owner: postgres
--

CREATE TABLE offers.user_segments (
    id bigint NOT NULL,
    customer_id bigint NOT NULL,
    segment_type offers.user_segment_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE offers.user_segments OWNER TO postgres;

--
-- Name: TABLE user_segments; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON TABLE offers.user_segments IS 'Explicit user segments for special cases (RECONCILIATION_USER). FIRST_TIME_USER/REGULAR_USER remain calculated on-the-fly.';


--
-- Name: COLUMN user_segments.customer_id; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.user_segments.customer_id IS 'Customer ID mapped to this segment';


--
-- Name: COLUMN user_segments.segment_type; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON COLUMN offers.user_segments.segment_type IS 'Type of segment. Currently only RECONCILIATION_USER is stored. Other types are calculated on-the-fly.';


--
-- Name: user_segments_id_seq; Type: SEQUENCE; Schema: offers; Owner: postgres
--

CREATE SEQUENCE offers.user_segments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE offers.user_segments_id_seq OWNER TO postgres;

--
-- Name: user_segments_id_seq; Type: SEQUENCE OWNED BY; Schema: offers; Owner: postgres
--

ALTER SEQUENCE offers.user_segments_id_seq OWNED BY offers.user_segments.id;


--
-- Name: volume_bonus_tracking; Type: TABLE; Schema: offers; Owner: postgres
--

CREATE TABLE offers.volume_bonus_tracking (
    tracking_id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id bigint NOT NULL,
    offer_id uuid NOT NULL,
    consultation_date timestamp with time zone NOT NULL,
    total_consultation_minutes integer DEFAULT 0,
    bonus_minutes_earned integer DEFAULT 0,
    bonus_minutes_used integer DEFAULT 0,
    bonus_minutes_remaining integer DEFAULT 0,
    period_type character varying(20) NOT NULL,
    period_start timestamp with time zone NOT NULL,
    period_end timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone
);


ALTER TABLE offers.volume_bonus_tracking OWNER TO postgres;

--
-- Name: TABLE volume_bonus_tracking; Type: COMMENT; Schema: offers; Owner: postgres
--

COMMENT ON TABLE offers.volume_bonus_tracking IS 'Tracks volume bonus earnings and usage';


--
-- Name: auth_schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_schema_migrations (
    version bigint NOT NULL,
    dirty boolean NOT NULL
);


ALTER TABLE public.auth_schema_migrations OWNER TO postgres;

--
-- Name: celery_taskmeta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.celery_taskmeta (
    id integer NOT NULL,
    task_id character varying(155),
    status character varying(50),
    result bytea,
    date_done timestamp without time zone,
    traceback text,
    name character varying(155),
    args bytea,
    kwargs bytea,
    worker character varying(155),
    retries integer,
    queue character varying(155)
);


ALTER TABLE public.celery_taskmeta OWNER TO postgres;

--
-- Name: celery_tasksetmeta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.celery_tasksetmeta (
    id integer NOT NULL,
    taskset_id character varying(155),
    result bytea,
    date_done timestamp without time zone
);


ALTER TABLE public.celery_tasksetmeta OWNER TO postgres;

--
-- Name: consultation_schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.consultation_schema_migrations (
    version bigint NOT NULL,
    dirty boolean NOT NULL
);


ALTER TABLE public.consultation_schema_migrations OWNER TO postgres;

--
-- Name: customers_schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers_schema_migrations (
    version bigint NOT NULL,
    dirty boolean NOT NULL
);


ALTER TABLE public.customers_schema_migrations OWNER TO postgres;

--
-- Name: guide_schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guide_schema_migrations (
    version bigint NOT NULL,
    dirty boolean NOT NULL
);


ALTER TABLE public.guide_schema_migrations OWNER TO postgres;

--
-- Name: notifications_schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications_schema_migrations (
    version bigint NOT NULL,
    dirty boolean NOT NULL
);


ALTER TABLE public.notifications_schema_migrations OWNER TO postgres;

--
-- Name: offers_schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.offers_schema_migrations (
    version bigint NOT NULL,
    dirty boolean NOT NULL
);


ALTER TABLE public.offers_schema_migrations OWNER TO postgres;

--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schema_migrations (
    version bigint NOT NULL,
    dirty boolean NOT NULL
);


ALTER TABLE public.schema_migrations OWNER TO postgres;

--
-- Name: task_id_sequence; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.task_id_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.task_id_sequence OWNER TO postgres;

--
-- Name: taskset_id_sequence; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.taskset_id_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.taskset_id_sequence OWNER TO postgres;

--
-- Name: alembic_version; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE wallet.alembic_version OWNER TO postgres;

--
-- Name: consultant_payouts; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.consultant_payouts (
    payout_id bigint NOT NULL,
    consultant_id bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    tds_amount numeric(10,2) NOT NULL,
    charges numeric(10,2) DEFAULT 0.00,
    payment_method wallet.payment_method DEFAULT 'WALLET'::wallet.payment_method NOT NULL,
    payment_reference character varying(255),
    payment_date timestamp without time zone,
    status wallet.payout_status DEFAULT 'PENDING'::wallet.payout_status,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE wallet.consultant_payouts OWNER TO postgres;

--
-- Name: consultant_payouts_payout_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.consultant_payouts_payout_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.consultant_payouts_payout_id_seq OWNER TO postgres;

--
-- Name: consultant_payouts_payout_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.consultant_payouts_payout_id_seq OWNED BY wallet.consultant_payouts.payout_id;


--
-- Name: consultant_wallets; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.consultant_wallets (
    consultant_id bigint NOT NULL,
    name character varying(255) NOT NULL,
    phone_number character varying(10) NOT NULL,
    specialization character varying(255),
    rating numeric(3,2),
    revenue_share integer,
    accepts_promotional_offers boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    CONSTRAINT check_consultant_wallets_phone_format CHECK (((phone_number)::text ~ '^[0-9]{10}$'::text)),
    CONSTRAINT consultant_wallets_revenue_share_check CHECK (((revenue_share >= 0) AND (revenue_share <= 100)))
);


ALTER TABLE wallet.consultant_wallets OWNER TO postgres;

--
-- Name: consultants; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.consultants (
    consultant_id bigint NOT NULL,
    name character varying(255) NOT NULL,
    tenant_id integer NOT NULL,
    specialization character varying(255),
    rating numeric(3,2),
    price_per_minute numeric(10,2),
    revenue_share numeric(10,2),
    accepts_promotional_offers boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    tenant_consultant_id character varying(255) NOT NULL,
    updated_at timestamp without time zone DEFAULT now(),
    phone_number character varying(10) NOT NULL,
    CONSTRAINT check_consultants_phone_format CHECK (((phone_number)::text ~ '^[0-9]{10}$'::text))
);


ALTER TABLE wallet.consultants OWNER TO postgres;

--
-- Name: consultants_consultant_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.consultants_consultant_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.consultants_consultant_id_seq OWNER TO postgres;

--
-- Name: consultants_consultant_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.consultants_consultant_id_seq OWNED BY wallet.consultants.consultant_id;


--
-- Name: coupons; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.coupons (
    coupon_id integer NOT NULL,
    coupon_code character varying(50) NOT NULL,
    description text NOT NULL,
    coupon_type wallet.coupon_type NOT NULL,
    value numeric(10,2) NOT NULL,
    max_discount_amount numeric(10,2),
    min_order_value numeric(10,2),
    valid_from timestamp without time zone,
    valid_to timestamp without time zone,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE wallet.coupons OWNER TO postgres;

--
-- Name: coupons_coupon_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.coupons_coupon_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.coupons_coupon_id_seq OWNER TO postgres;

--
-- Name: coupons_coupon_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.coupons_coupon_id_seq OWNED BY wallet.coupons.coupon_id;


--
-- Name: invoice_line_items; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.invoice_line_items (
    line_item_id bigint NOT NULL,
    invoice_id bigint NOT NULL,
    description text NOT NULL,
    total numeric(10,2) NOT NULL,
    discount numeric(10,2) DEFAULT 0.00,
    taxable_value numeric(10,2) NOT NULL,
    sgst_rate numeric(5,2) DEFAULT 0.00,
    sgst_amount numeric(10,2) DEFAULT 0.00,
    cgst_rate numeric(5,2) DEFAULT 0.00,
    cgst_amount numeric(10,2) DEFAULT 0.00,
    igst_rate numeric(5,2) DEFAULT 0.00,
    igst_amount numeric(10,2) DEFAULT 0.00
);


ALTER TABLE wallet.invoice_line_items OWNER TO postgres;

--
-- Name: invoice_line_items_line_item_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.invoice_line_items_line_item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.invoice_line_items_line_item_id_seq OWNER TO postgres;

--
-- Name: invoice_line_items_line_item_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.invoice_line_items_line_item_id_seq OWNED BY wallet.invoice_line_items.line_item_id;


--
-- Name: invoices; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.invoices (
    invoice_id bigint NOT NULL,
    user_id bigint NOT NULL,
    payment_order_id bigint NOT NULL,
    transaction_id character varying(50) NOT NULL,
    payment_id character varying(50),
    invoice_number character varying(50) NOT NULL,
    invoice_url character varying(512),
    invoice_date timestamp without time zone NOT NULL,
    recipient_gstin character varying(15),
    place_of_supply character varying(50) NOT NULL,
    company_name character varying(255),
    company_gstin character varying(15),
    company_address text,
    company_website character varying(255),
    total_value numeric(15,2) NOT NULL,
    total_discount numeric(15,2) DEFAULT 0.00,
    total_taxable_value numeric(15,2) NOT NULL,
    total_sgst numeric(15,2) DEFAULT 0.00,
    total_cgst numeric(15,2) DEFAULT 0.00,
    total_igst numeric(15,2) DEFAULT 0.00,
    total_tax numeric(15,2) NOT NULL,
    total_amount numeric(15,2) NOT NULL,
    total_amount_words text NOT NULL,
    hsn_sac character varying(20),
    reverse_charge boolean,
    pan_number character varying(10),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    customer_info jsonb NOT NULL
);


ALTER TABLE wallet.invoices OWNER TO postgres;

--
-- Name: COLUMN invoices.company_gstin; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.invoices.company_gstin IS 'Company GSTIN. Application default updated to ''29AAPCP2115F1ZE'' on 2025-09-03.';


--
-- Name: COLUMN invoices.company_address; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.invoices.company_address IS 'Company address. Application default updated to ''PixelForgeTech Private Limited, Building No./Flat No.: No 235 Road/Street: 13th Cross, Hoyasala Nagar 2nd Stage, Indiranagar, Bengaluru, Karnataka, PIN Code: 560038'' on 2025-09-03.';


--
-- Name: COLUMN invoices.pan_number; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.invoices.pan_number IS 'Company PAN number. Application default updated to ''AAPCP2115F'' on 2025-09-03.';


--
-- Name: COLUMN invoices.customer_info; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.invoices.customer_info IS 'JSONB column containing customer information including name, address, and other flexible customer data';


--
-- Name: invoices_invoice_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.invoices_invoice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.invoices_invoice_id_seq OWNER TO postgres;

--
-- Name: invoices_invoice_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.invoices_invoice_id_seq OWNED BY wallet.invoices.invoice_id;


--
-- Name: kombu_message; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.kombu_message (
    id integer NOT NULL,
    visible boolean,
    "timestamp" timestamp without time zone,
    payload text NOT NULL,
    version smallint NOT NULL,
    queue_id integer
);


ALTER TABLE wallet.kombu_message OWNER TO postgres;

--
-- Name: kombu_queue; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.kombu_queue (
    id integer NOT NULL,
    name character varying(200)
);


ALTER TABLE wallet.kombu_queue OWNER TO postgres;

--
-- Name: message_id_sequence; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.message_id_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.message_id_sequence OWNER TO postgres;

--
-- Name: payment_gateways; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.payment_gateways (
    gateway_id integer NOT NULL,
    name character varying(255) NOT NULL,
    is_active boolean DEFAULT true
);


ALTER TABLE wallet.payment_gateways OWNER TO postgres;

--
-- Name: payment_gateways_gateway_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.payment_gateways_gateway_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.payment_gateways_gateway_id_seq OWNER TO postgres;

--
-- Name: payment_gateways_gateway_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.payment_gateways_gateway_id_seq OWNED BY wallet.payment_gateways.gateway_id;


--
-- Name: payment_orders; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.payment_orders (
    payment_order_id bigint NOT NULL,
    user_id bigint NOT NULL,
    gateway_id integer NOT NULL,
    amount numeric(15,2) NOT NULL,
    tax_amount numeric(15,2) NOT NULL,
    virtual_cash_amount numeric(15,2) NOT NULL,
    currency character varying(3) DEFAULT 'INR'::character varying NOT NULL,
    status wallet.payment_order_status DEFAULT 'PENDING'::wallet.payment_order_status NOT NULL,
    info jsonb,
    payment_method wallet.payment_methods NOT NULL,
    gateway_order_id character varying NOT NULL,
    wallet_credited boolean DEFAULT false NOT NULL,
    task_id character varying(255),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    is_external_payment boolean DEFAULT false NOT NULL,
    external_reference_id character varying(255),
    external_gateway character varying(255),
    payment_date timestamp without time zone,
    offer_applied jsonb
);


ALTER TABLE wallet.payment_orders OWNER TO postgres;

--
-- Name: COLUMN payment_orders.offer_applied; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.payment_orders.offer_applied IS 'JSONB metadata containing offer details applied to this payment/recharge order (for offer type ''recharge'')';


--
-- Name: payment_orders_payment_order_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.payment_orders_payment_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.payment_orders_payment_order_id_seq OWNER TO postgres;

--
-- Name: payment_orders_payment_order_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.payment_orders_payment_order_id_seq OWNED BY wallet.payment_orders.payment_order_id;


--
-- Name: payment_transactions; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.payment_transactions (
    payment_transaction_id bigint NOT NULL,
    payment_order_id bigint NOT NULL,
    gateway_transaction_id character varying(255) NOT NULL,
    gateway_response jsonb NOT NULL,
    status character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE wallet.payment_transactions OWNER TO postgres;

--
-- Name: payment_transactions_payment_transaction_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.payment_transactions_payment_transaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.payment_transactions_payment_transaction_id_seq OWNER TO postgres;

--
-- Name: payment_transactions_payment_transaction_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.payment_transactions_payment_transaction_id_seq OWNED BY wallet.payment_transactions.payment_transaction_id;


--
-- Name: promotion_rules; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.promotion_rules (
    rule_id integer NOT NULL,
    name character varying(255) NOT NULL,
    min_recharge_amount numeric(15,2),
    max_recharge_amount numeric(15,2),
    virtual_cash_percentage numeric(5,2) NOT NULL,
    is_active boolean DEFAULT true,
    user_types text[] NOT NULL,
    CONSTRAINT check_min_max_recharge CHECK ((min_recharge_amount <= max_recharge_amount)),
    CONSTRAINT check_user_types_not_empty CHECK ((array_length(user_types, 1) > 0))
);


ALTER TABLE wallet.promotion_rules OWNER TO postgres;

--
-- Name: TABLE promotion_rules; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON TABLE wallet.promotion_rules IS 'Promotion rules now support fixed recharge amounts. When min_recharge_amount equals max_recharge_amount, it represents a fixed recharge option. Max virtual cash per transaction is capped at ₹7500. Virtual cash is calculated but never exceeds ₹7500 per transaction.';


--
-- Name: COLUMN promotion_rules.user_types; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.promotion_rules.user_types IS 'Array of user types this promotion applies to. Must be non-empty. Supported types: first_time, regular, premium, vip. Example: [''first_time'', ''regular''] means rule applies to both user types.';


--
-- Name: promotion_rules_rule_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.promotion_rules_rule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.promotion_rules_rule_id_seq OWNER TO postgres;

--
-- Name: promotion_rules_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.promotion_rules_rule_id_seq OWNED BY wallet.promotion_rules.rule_id;


--
-- Name: queue_id_sequence; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.queue_id_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.queue_id_sequence OWNER TO postgres;

--
-- Name: quick_connect_rates; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.quick_connect_rates (
    rate_id integer NOT NULL,
    mode character varying(10) NOT NULL,
    rate_per_minute numeric(10,2) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT quick_connect_rates_mode_check CHECK (((mode)::text = ANY (ARRAY[('CHAT'::character varying)::text, ('CALL'::character varying)::text]))),
    CONSTRAINT quick_connect_rates_rate_per_minute_check CHECK ((rate_per_minute > (0)::numeric))
);


ALTER TABLE wallet.quick_connect_rates OWNER TO postgres;

--
-- Name: TABLE quick_connect_rates; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON TABLE wallet.quick_connect_rates IS 'Fixed rates for quick connect consultations per mode';


--
-- Name: quick_connect_rates_rate_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.quick_connect_rates_rate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.quick_connect_rates_rate_id_seq OWNER TO postgres;

--
-- Name: quick_connect_rates_rate_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.quick_connect_rates_rate_id_seq OWNED BY wallet.quick_connect_rates.rate_id;


--
-- Name: refund_audit; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.refund_audit (
    id bigint NOT NULL,
    consultation_id bigint NOT NULL,
    customer_wallet_user_id bigint NOT NULL,
    amount_refunded numeric(10,2) DEFAULT 0.00 NOT NULL,
    real_cash_refunded numeric(10,2) DEFAULT 0.00 NOT NULL,
    virtual_cash_refunded numeric(10,2) DEFAULT 0.00 NOT NULL,
    refund_status wallet.refund_status DEFAULT 'INITIATED'::wallet.refund_status NOT NULL,
    initiated_by character varying(100),
    initiated_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone,
    error_message text,
    retry_count integer DEFAULT 0 NOT NULL,
    refund_metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT check_amount_positive CHECK ((amount_refunded >= (0)::numeric)),
    CONSTRAINT check_amounts_sum CHECK ((amount_refunded = (real_cash_refunded + virtual_cash_refunded))),
    CONSTRAINT check_real_cash_positive CHECK ((real_cash_refunded >= (0)::numeric)),
    CONSTRAINT check_virtual_cash_positive CHECK ((virtual_cash_refunded >= (0)::numeric))
);


ALTER TABLE wallet.refund_audit OWNER TO postgres;

--
-- Name: TABLE refund_audit; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON TABLE wallet.refund_audit IS 'Audit trail for consultation refunds in the refund reconciliation system';


--
-- Name: COLUMN refund_audit.consultation_id; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.refund_audit.consultation_id IS 'Reference to consultation.consultation(id)';


--
-- Name: COLUMN refund_audit.customer_wallet_user_id; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.refund_audit.customer_wallet_user_id IS 'Wallet user ID of the customer receiving the refund';


--
-- Name: COLUMN refund_audit.real_cash_refunded; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.refund_audit.real_cash_refunded IS 'Amount of real cash refunded to wallet balance';


--
-- Name: COLUMN refund_audit.virtual_cash_refunded; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.refund_audit.virtual_cash_refunded IS 'Amount converted to reconciliation voucher (if applicable)';


--
-- Name: COLUMN refund_audit.initiated_by; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.refund_audit.initiated_by IS 'Who initiated the refund: system (auto) or admin user identifier';


--
-- Name: COLUMN refund_audit.refund_metadata; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.refund_audit.refund_metadata IS 'Additional metadata like offer_id, voucher_reservation_id, workflow_id';


--
-- Name: refund_audit_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.refund_audit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.refund_audit_id_seq OWNER TO postgres;

--
-- Name: refund_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.refund_audit_id_seq OWNED BY wallet.refund_audit.id;


--
-- Name: tenants; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.tenants (
    id integer NOT NULL,
    name character varying NOT NULL,
    hashed_api_key character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE wallet.tenants OWNER TO postgres;

--
-- Name: tenants_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.tenants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.tenants_id_seq OWNER TO postgres;

--
-- Name: tenants_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.tenants_id_seq OWNED BY wallet.tenants.id;


--
-- Name: user_wallets; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.user_wallets (
    user_id bigint NOT NULL,
    email character varying(255),
    name character varying(255),
    country_code character varying(10),
    phone_number character varying(10) NOT NULL,
    real_cash numeric(15,2) DEFAULT 0.00,
    virtual_cash numeric(15,2) DEFAULT 0.00,
    cumulative_sum numeric(15,2) DEFAULT 0.00,
    recharge_count integer DEFAULT 0,
    info jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_login timestamp without time zone,
    is_locked boolean DEFAULT false,
    deleted_at timestamp without time zone,
    CONSTRAINT check_user_wallets_phone_format CHECK (((phone_number)::text ~ '^[0-9]{10}$'::text)),
    CONSTRAINT chk_user_cumulative_sum_non_negative CHECK ((cumulative_sum >= (0)::numeric)),
    CONSTRAINT chk_user_real_cash_non_negative CHECK ((real_cash >= (0)::numeric)),
    CONSTRAINT chk_user_virtual_cash_non_negative CHECK ((virtual_cash >= (0)::numeric))
);


ALTER TABLE wallet.user_wallets OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.users (
    user_id bigint NOT NULL,
    email character varying(255),
    name character varying(255),
    country_code character varying(10),
    created_at timestamp without time zone DEFAULT now(),
    last_login timestamp without time zone,
    is_locked boolean DEFAULT false,
    tenant_id integer NOT NULL,
    tenant_user_id character varying(255) NOT NULL,
    updated_at timestamp without time zone DEFAULT now(),
    phone_number character varying(10) NOT NULL,
    info jsonb,
    CONSTRAINT check_users_phone_format CHECK (((phone_number)::text ~ '^[0-9]{10}$'::text))
);


ALTER TABLE wallet.users OWNER TO postgres;

--
-- Name: COLUMN users.info; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.users.info IS 'Flexible JSONB column for storing additional user metadata and preferences';


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.users_user_id_seq OWNED BY wallet.users.user_id;


--
-- Name: wallet_orders; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.wallet_orders (
    order_id bigint NOT NULL,
    user_id bigint NOT NULL,
    consultant_id bigint,
    payout_id bigint,
    service_type wallet.service_type NOT NULL,
    minutes_ordered integer,
    seconds_ordered integer,
    max_duration_minutes integer NOT NULL,
    max_duration_seconds integer NOT NULL,
    price_per_minute numeric(10,2),
    total_mrp numeric(10,2) NOT NULL,
    discount numeric(10,2),
    final_amount numeric(10,2) NOT NULL,
    status wallet.order_status NOT NULL,
    status_reason text,
    created_at timestamp without time zone DEFAULT now(),
    completed_at timestamp without time zone,
    consultant_share numeric(10,2),
    consultant_share_percent numeric(5,2),
    consultant_paid boolean DEFAULT false,
    consultant_payment_date timestamp without time zone,
    is_quick_connect_order boolean DEFAULT false,
    context_id character varying(255),
    promotional boolean DEFAULT false NOT NULL,
    free boolean DEFAULT false NOT NULL,
    offer_metadata jsonb,
    is_refunded boolean DEFAULT false NOT NULL,
    CONSTRAINT check_discount_non_negative CHECK ((discount >= (0)::numeric))
);


ALTER TABLE wallet.wallet_orders OWNER TO postgres;

--
-- Name: COLUMN wallet_orders.is_quick_connect_order; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.wallet_orders.is_quick_connect_order IS 'Flag to identify quick connect orders vs regular orders';


--
-- Name: COLUMN wallet_orders.promotional; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.wallet_orders.promotional IS 'Flag indicating if this order used a promotional offer';


--
-- Name: COLUMN wallet_orders.free; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.wallet_orders.free IS 'Flag indicating if this order was free (e.g., free minutes voucher)';


--
-- Name: COLUMN wallet_orders.offer_metadata; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.wallet_orders.offer_metadata IS 'JSONB metadata containing offer details applied to this order (rate_card, discounts, base_rate, etc.)';


--
-- Name: COLUMN wallet_orders.is_refunded; Type: COMMENT; Schema: wallet; Owner: postgres
--

COMMENT ON COLUMN wallet.wallet_orders.is_refunded IS 'Marks whether this order has been refunded through the refund reconciliation system';


--
-- Name: wallet_orders_order_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.wallet_orders_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.wallet_orders_order_id_seq OWNER TO postgres;

--
-- Name: wallet_orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.wallet_orders_order_id_seq OWNED BY wallet.wallet_orders.order_id;


--
-- Name: wallet_settings; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.wallet_settings (
    setting_id integer NOT NULL,
    setting_key character varying(100) NOT NULL,
    setting_value text NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE wallet.wallet_settings OWNER TO postgres;

--
-- Name: wallet_settings_setting_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.wallet_settings_setting_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.wallet_settings_setting_id_seq OWNER TO postgres;

--
-- Name: wallet_settings_setting_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.wallet_settings_setting_id_seq OWNED BY wallet.wallet_settings.setting_id;


--
-- Name: wallet_transactions; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.wallet_transactions (
    transaction_id character varying(255) NOT NULL,
    id bigint,
    user_id bigint NOT NULL,
    invoice_id bigint,
    gateway_id integer,
    order_id bigint,
    type wallet.transaction_type NOT NULL,
    amount numeric(15,2),
    real_cash_delta numeric(15,2),
    virtual_cash_delta numeric(15,2),
    cumulative_real numeric(15,2),
    cumulative_virtual numeric(15,2),
    cumulative_total numeric(15,2),
    currency character varying(3) DEFAULT 'INR'::character varying,
    gateway_transaction_id character varying(255),
    is_promotional boolean DEFAULT false,
    comment text,
    receipt_url character varying(512),
    payment_order_paid_amount numeric(15,2),
    tax_deducted numeric(15,2),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE wallet.wallet_transactions OWNER TO postgres;

--
-- Name: wallets; Type: TABLE; Schema: wallet; Owner: postgres
--

CREATE TABLE wallet.wallets (
    wallet_id bigint NOT NULL,
    user_id bigint,
    real_cash numeric(15,2) DEFAULT 0.00,
    virtual_cash numeric(15,2) DEFAULT 0.00,
    cumulative_sum numeric(15,2) DEFAULT 0.00,
    recharge_count integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT chk_cumulative_sum_non_negative CHECK ((cumulative_sum >= (0)::numeric)),
    CONSTRAINT chk_real_cash_non_negative CHECK ((real_cash >= (0)::numeric)),
    CONSTRAINT chk_virtual_cash_non_negative CHECK ((virtual_cash >= (0)::numeric))
);


ALTER TABLE wallet.wallets OWNER TO postgres;

--
-- Name: wallets_wallet_id_seq; Type: SEQUENCE; Schema: wallet; Owner: postgres
--

CREATE SEQUENCE wallet.wallets_wallet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE wallet.wallets_wallet_id_seq OWNER TO postgres;

--
-- Name: wallets_wallet_id_seq; Type: SEQUENCE OWNED BY; Schema: wallet; Owner: postgres
--

ALTER SEQUENCE wallet.wallets_wallet_id_seq OWNED BY wallet.wallets.wallet_id;


--
-- Name: admin_users id; Type: DEFAULT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_users ALTER COLUMN id SET DEFAULT nextval('admin.admin_users_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.audit_logs ALTER COLUMN id SET DEFAULT nextval('admin.audit_logs_id_seq'::regclass);


--
-- Name: auth_user_roles id; Type: DEFAULT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.auth_user_roles ALTER COLUMN id SET DEFAULT nextval('auth.auth_user_roles_id_seq'::regclass);


--
-- Name: auth_users id; Type: DEFAULT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.auth_users ALTER COLUMN id SET DEFAULT nextval('auth.auth_users_id_seq'::regclass);


--
-- Name: casbin_rules id; Type: DEFAULT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.casbin_rules ALTER COLUMN id SET DEFAULT nextval('auth.casbin_rules_id_seq'::regclass);


--
-- Name: login_activities id; Type: DEFAULT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.login_activities ALTER COLUMN id SET DEFAULT nextval('auth.login_activities_id_seq'::regclass);


--
-- Name: otp_attempts id; Type: DEFAULT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.otp_attempts ALTER COLUMN id SET DEFAULT nextval('auth.otp_attempts_id_seq'::regclass);


--
-- Name: user_devices id; Type: DEFAULT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.user_devices ALTER COLUMN id SET DEFAULT nextval('auth.user_devices_id_seq'::regclass);


--
-- Name: user_sessions id; Type: DEFAULT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.user_sessions ALTER COLUMN id SET DEFAULT nextval('auth.user_sessions_id_seq'::regclass);


--
-- Name: consultation id; Type: DEFAULT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.consultation ALTER COLUMN id SET DEFAULT nextval('consultation.consultation_id_seq'::regclass);


--
-- Name: consultation_quality_metrics id; Type: DEFAULT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.consultation_quality_metrics ALTER COLUMN id SET DEFAULT nextval('consultation.consultation_quality_metrics_id_seq'::regclass);


--
-- Name: feedback id; Type: DEFAULT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.feedback ALTER COLUMN id SET DEFAULT nextval('consultation.feedback_id_seq'::regclass);


--
-- Name: feedback_comments_by_guide id; Type: DEFAULT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.feedback_comments_by_guide ALTER COLUMN id SET DEFAULT nextval('consultation.feedback_comments_by_guide_id_seq'::regclass);


--
-- Name: address address_id; Type: DEFAULT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.address ALTER COLUMN address_id SET DEFAULT nextval('customers.address_address_id_seq'::regclass);


--
-- Name: customer customer_id; Type: DEFAULT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.customer ALTER COLUMN customer_id SET DEFAULT nextval('customers.customer_customer_id_seq'::regclass);


--
-- Name: customer_address customer_address_id; Type: DEFAULT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.customer_address ALTER COLUMN customer_address_id SET DEFAULT nextval('customers.customer_address_customer_address_id_seq'::regclass);


--
-- Name: customer_profile profile_id; Type: DEFAULT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.customer_profile ALTER COLUMN profile_id SET DEFAULT nextval('customers.customer_profile_profile_id_seq'::regclass);


--
-- Name: addresses id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.addresses ALTER COLUMN id SET DEFAULT nextval('guide.addresses_id_seq'::regclass);


--
-- Name: agreement id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.agreement ALTER COLUMN id SET DEFAULT nextval('guide.agreement_id_seq'::regclass);


--
-- Name: bank_account id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.bank_account ALTER COLUMN id SET DEFAULT nextval('guide.bank_account_id_seq'::regclass);


--
-- Name: guide_profile id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_profile ALTER COLUMN id SET DEFAULT nextval('guide.guide_profile_id_seq'::regclass);


--
-- Name: guide_profile_audit id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_profile_audit ALTER COLUMN id SET DEFAULT nextval('guide.guide_profile_audit_id_seq'::regclass);


--
-- Name: kyc_document id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.kyc_document ALTER COLUMN id SET DEFAULT nextval('guide.kyc_document_id_seq'::regclass);


--
-- Name: languages id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.languages ALTER COLUMN id SET DEFAULT nextval('guide.languages_id_seq'::regclass);


--
-- Name: media id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.media ALTER COLUMN id SET DEFAULT nextval('guide.media_id_seq'::regclass);


--
-- Name: saved_messages id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.saved_messages ALTER COLUMN id SET DEFAULT nextval('guide.saved_messages_id_seq'::regclass);


--
-- Name: skills id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.skills ALTER COLUMN id SET DEFAULT nextval('guide.skills_id_seq'::regclass);


--
-- Name: verification id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.verification ALTER COLUMN id SET DEFAULT nextval('guide.verification_id_seq'::regclass);


--
-- Name: verification_audit_log id; Type: DEFAULT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.verification_audit_log ALTER COLUMN id SET DEFAULT nextval('guide.verification_audit_log_id_seq'::regclass);


--
-- Name: leads id; Type: DEFAULT; Schema: marketing; Owner: postgres
--

ALTER TABLE ONLY marketing.leads ALTER COLUMN id SET DEFAULT nextval('marketing.leads_id_seq'::regclass);


--
-- Name: user_segments id; Type: DEFAULT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.user_segments ALTER COLUMN id SET DEFAULT nextval('offers.user_segments_id_seq'::regclass);


--
-- Name: consultant_payouts payout_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.consultant_payouts ALTER COLUMN payout_id SET DEFAULT nextval('wallet.consultant_payouts_payout_id_seq'::regclass);


--
-- Name: consultants consultant_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.consultants ALTER COLUMN consultant_id SET DEFAULT nextval('wallet.consultants_consultant_id_seq'::regclass);


--
-- Name: coupons coupon_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.coupons ALTER COLUMN coupon_id SET DEFAULT nextval('wallet.coupons_coupon_id_seq'::regclass);


--
-- Name: invoice_line_items line_item_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.invoice_line_items ALTER COLUMN line_item_id SET DEFAULT nextval('wallet.invoice_line_items_line_item_id_seq'::regclass);


--
-- Name: invoices invoice_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.invoices ALTER COLUMN invoice_id SET DEFAULT nextval('wallet.invoices_invoice_id_seq'::regclass);


--
-- Name: payment_gateways gateway_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_gateways ALTER COLUMN gateway_id SET DEFAULT nextval('wallet.payment_gateways_gateway_id_seq'::regclass);


--
-- Name: payment_orders payment_order_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_orders ALTER COLUMN payment_order_id SET DEFAULT nextval('wallet.payment_orders_payment_order_id_seq'::regclass);


--
-- Name: payment_transactions payment_transaction_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_transactions ALTER COLUMN payment_transaction_id SET DEFAULT nextval('wallet.payment_transactions_payment_transaction_id_seq'::regclass);


--
-- Name: promotion_rules rule_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.promotion_rules ALTER COLUMN rule_id SET DEFAULT nextval('wallet.promotion_rules_rule_id_seq'::regclass);


--
-- Name: quick_connect_rates rate_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.quick_connect_rates ALTER COLUMN rate_id SET DEFAULT nextval('wallet.quick_connect_rates_rate_id_seq'::regclass);


--
-- Name: refund_audit id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.refund_audit ALTER COLUMN id SET DEFAULT nextval('wallet.refund_audit_id_seq'::regclass);


--
-- Name: tenants id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.tenants ALTER COLUMN id SET DEFAULT nextval('wallet.tenants_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.users ALTER COLUMN user_id SET DEFAULT nextval('wallet.users_user_id_seq'::regclass);


--
-- Name: wallet_orders order_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_orders ALTER COLUMN order_id SET DEFAULT nextval('wallet.wallet_orders_order_id_seq'::regclass);


--
-- Name: wallet_settings setting_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_settings ALTER COLUMN setting_id SET DEFAULT nextval('wallet.wallet_settings_setting_id_seq'::regclass);


--
-- Name: wallets wallet_id; Type: DEFAULT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallets ALTER COLUMN wallet_id SET DEFAULT nextval('wallet.wallets_wallet_id_seq'::regclass);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: admin; Owner: postgres
--

ALTER TABLE ONLY admin.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: auth_user_roles auth_user_roles_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.auth_user_roles
    ADD CONSTRAINT auth_user_roles_pkey PRIMARY KEY (id);


--
-- Name: auth_users auth_users_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.auth_users
    ADD CONSTRAINT auth_users_pkey PRIMARY KEY (id);


--
-- Name: casbin_rules casbin_rules_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.casbin_rules
    ADD CONSTRAINT casbin_rules_pkey PRIMARY KEY (id);


--
-- Name: login_activities login_activities_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.login_activities
    ADD CONSTRAINT login_activities_pkey PRIMARY KEY (id);


--
-- Name: otp_attempts otp_attempts_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.otp_attempts
    ADD CONSTRAINT otp_attempts_pkey PRIMARY KEY (id);


--
-- Name: user_devices user_devices_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.user_devices
    ADD CONSTRAINT user_devices_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- Name: agora_consultation_session agora_consultation_session_pkey; Type: CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.agora_consultation_session
    ADD CONSTRAINT agora_consultation_session_pkey PRIMARY KEY (id);


--
-- Name: agora_webhook_events agora_webhook_events_pkey; Type: CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.agora_webhook_events
    ADD CONSTRAINT agora_webhook_events_pkey PRIMARY KEY (id);


--
-- Name: consultation consultation_pkey; Type: CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.consultation
    ADD CONSTRAINT consultation_pkey PRIMARY KEY (id);


--
-- Name: consultation_quality_metrics consultation_quality_metrics_pkey; Type: CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.consultation_quality_metrics
    ADD CONSTRAINT consultation_quality_metrics_pkey PRIMARY KEY (id);


--
-- Name: feedback_comments_by_guide feedback_comments_by_guide_pkey; Type: CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.feedback_comments_by_guide
    ADD CONSTRAINT feedback_comments_by_guide_pkey PRIMARY KEY (id);


--
-- Name: feedback feedback_pkey; Type: CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (id);


--
-- Name: consultation_quality_metrics unique_consultation_metrics; Type: CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.consultation_quality_metrics
    ADD CONSTRAINT unique_consultation_metrics UNIQUE (consultation_id);


--
-- Name: address address_pkey; Type: CONSTRAINT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.address
    ADD CONSTRAINT address_pkey PRIMARY KEY (address_id);


--
-- Name: customer_address customer_address_pkey; Type: CONSTRAINT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.customer_address
    ADD CONSTRAINT customer_address_pkey PRIMARY KEY (customer_address_id);


--
-- Name: customer customer_pkey; Type: CONSTRAINT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.customer
    ADD CONSTRAINT customer_pkey PRIMARY KEY (customer_id);


--
-- Name: customer_profile customer_profile_pkey; Type: CONSTRAINT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.customer_profile
    ADD CONSTRAINT customer_profile_pkey PRIMARY KEY (profile_id);


--
-- Name: customer_address unique_customer_address_link; Type: CONSTRAINT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.customer_address
    ADD CONSTRAINT unique_customer_address_link UNIQUE (customer_id, address_id);


--
-- Name: addresses addresses_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (id);


--
-- Name: agreement agreement_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.agreement
    ADD CONSTRAINT agreement_pkey PRIMARY KEY (id);


--
-- Name: bank_account bank_account_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.bank_account
    ADD CONSTRAINT bank_account_pkey PRIMARY KEY (id);


--
-- Name: guide_languages guide_languages_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_languages
    ADD CONSTRAINT guide_languages_pkey PRIMARY KEY (guide_id, language_id);


--
-- Name: guide_profile_audit guide_profile_audit_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_profile_audit
    ADD CONSTRAINT guide_profile_audit_pkey PRIMARY KEY (id);


--
-- Name: guide_profile guide_profile_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_profile
    ADD CONSTRAINT guide_profile_pkey PRIMARY KEY (id);


--
-- Name: guide_profile guide_profile_referral_code_key; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_profile
    ADD CONSTRAINT guide_profile_referral_code_key UNIQUE (referral_code);


--
-- Name: guide_skills guide_skills_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_skills
    ADD CONSTRAINT guide_skills_pkey PRIMARY KEY (guide_id, skill_id);


--
-- Name: kyc_document kyc_document_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.kyc_document
    ADD CONSTRAINT kyc_document_pkey PRIMARY KEY (id);


--
-- Name: languages languages_name_key; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.languages
    ADD CONSTRAINT languages_name_key UNIQUE (name);


--
-- Name: languages languages_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.languages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (id);


--
-- Name: media media_guide_id_cdn_url_key; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.media
    ADD CONSTRAINT media_guide_id_cdn_url_key UNIQUE (guide_id, cdn_url);


--
-- Name: media media_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.media
    ADD CONSTRAINT media_pkey PRIMARY KEY (id);


--
-- Name: saved_messages saved_messages_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.saved_messages
    ADD CONSTRAINT saved_messages_pkey PRIMARY KEY (id);


--
-- Name: skills skills_name_key; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.skills
    ADD CONSTRAINT skills_name_key UNIQUE (name);


--
-- Name: skills skills_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.skills
    ADD CONSTRAINT skills_pkey PRIMARY KEY (id);


--
-- Name: verification_audit_log verification_audit_log_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.verification_audit_log
    ADD CONSTRAINT verification_audit_log_pkey PRIMARY KEY (id);


--
-- Name: verification verification_pkey; Type: CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.verification
    ADD CONSTRAINT verification_pkey PRIMARY KEY (id);


--
-- Name: leads leads_phone_unique; Type: CONSTRAINT; Schema: marketing; Owner: postgres
--

ALTER TABLE ONLY marketing.leads
    ADD CONSTRAINT leads_phone_unique UNIQUE (phone);


--
-- Name: leads leads_pkey; Type: CONSTRAINT; Schema: marketing; Owner: postgres
--

ALTER TABLE ONLY marketing.leads
    ADD CONSTRAINT leads_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: marketing; Owner: postgres
--

ALTER TABLE ONLY marketing.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (type, key);


--
-- Name: client_events client_events_event_id_key; Type: CONSTRAINT; Schema: notifications; Owner: postgres
--

ALTER TABLE ONLY notifications.client_events
    ADD CONSTRAINT client_events_event_id_key UNIQUE (event_id);


--
-- Name: client_events client_events_pkey; Type: CONSTRAINT; Schema: notifications; Owner: postgres
--

ALTER TABLE ONLY notifications.client_events
    ADD CONSTRAINT client_events_pkey PRIMARY KEY (id);


--
-- Name: delivery_attempts delivery_attempts_pkey; Type: CONSTRAINT; Schema: notifications; Owner: postgres
--

ALTER TABLE ONLY notifications.delivery_attempts
    ADD CONSTRAINT delivery_attempts_pkey PRIMARY KEY (id);


--
-- Name: escalation_rules escalation_rules_pkey; Type: CONSTRAINT; Schema: notifications; Owner: postgres
--

ALTER TABLE ONLY notifications.escalation_rules
    ADD CONSTRAINT escalation_rules_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: notifications; Owner: postgres
--

ALTER TABLE ONLY notifications.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (event_id);


--
-- Name: consultant_rates consultant_rates_pkey; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.consultant_rates
    ADD CONSTRAINT consultant_rates_pkey PRIMARY KEY (rate_id);


--
-- Name: offer_campaigns offer_campaigns_pkey; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.offer_campaigns
    ADD CONSTRAINT offer_campaigns_pkey PRIMARY KEY (campaign_id);


--
-- Name: offer_consumptions offer_consumptions_pkey; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.offer_consumptions
    ADD CONSTRAINT offer_consumptions_pkey PRIMARY KEY (consumption_id);


--
-- Name: offer_definitions offer_definitions_pkey; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.offer_definitions
    ADD CONSTRAINT offer_definitions_pkey PRIMARY KEY (offer_id);


--
-- Name: offer_reservations offer_reservations_pkey; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.offer_reservations
    ADD CONSTRAINT offer_reservations_pkey PRIMARY KEY (reservation_id);


--
-- Name: user_segments uk_user_segments_customer_segment; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.user_segments
    ADD CONSTRAINT uk_user_segments_customer_segment UNIQUE (customer_id, segment_type);


--
-- Name: offer_consumptions unique_consumption_payment_order; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.offer_consumptions
    ADD CONSTRAINT unique_consumption_payment_order UNIQUE (payment_order_id);


--
-- Name: offer_reservations unique_reservation_payment_order; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.offer_reservations
    ADD CONSTRAINT unique_reservation_payment_order UNIQUE (payment_order_id);


--
-- Name: user_milestone_progress unique_user_offer_milestone; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.user_milestone_progress
    ADD CONSTRAINT unique_user_offer_milestone UNIQUE (user_id, offer_id);


--
-- Name: user_behavior_metrics user_behavior_metrics_pkey; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.user_behavior_metrics
    ADD CONSTRAINT user_behavior_metrics_pkey PRIMARY KEY (user_id);


--
-- Name: user_milestone_progress user_milestone_progress_pkey; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.user_milestone_progress
    ADD CONSTRAINT user_milestone_progress_pkey PRIMARY KEY (progress_id);


--
-- Name: user_segments user_segments_pkey; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.user_segments
    ADD CONSTRAINT user_segments_pkey PRIMARY KEY (id);


--
-- Name: volume_bonus_tracking volume_bonus_tracking_pkey; Type: CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.volume_bonus_tracking
    ADD CONSTRAINT volume_bonus_tracking_pkey PRIMARY KEY (tracking_id);


--
-- Name: auth_schema_migrations auth_schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_schema_migrations
    ADD CONSTRAINT auth_schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: celery_taskmeta celery_taskmeta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.celery_taskmeta
    ADD CONSTRAINT celery_taskmeta_pkey PRIMARY KEY (id);


--
-- Name: celery_taskmeta celery_taskmeta_task_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.celery_taskmeta
    ADD CONSTRAINT celery_taskmeta_task_id_key UNIQUE (task_id);


--
-- Name: celery_tasksetmeta celery_tasksetmeta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.celery_tasksetmeta
    ADD CONSTRAINT celery_tasksetmeta_pkey PRIMARY KEY (id);


--
-- Name: celery_tasksetmeta celery_tasksetmeta_taskset_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.celery_tasksetmeta
    ADD CONSTRAINT celery_tasksetmeta_taskset_id_key UNIQUE (taskset_id);


--
-- Name: consultation_schema_migrations consultation_schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consultation_schema_migrations
    ADD CONSTRAINT consultation_schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: customers_schema_migrations customers_schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers_schema_migrations
    ADD CONSTRAINT customers_schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: guide_schema_migrations guide_schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guide_schema_migrations
    ADD CONSTRAINT guide_schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: notifications_schema_migrations notifications_schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications_schema_migrations
    ADD CONSTRAINT notifications_schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: offers_schema_migrations offers_schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.offers_schema_migrations
    ADD CONSTRAINT offers_schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: quick_connect_rates chk_one_active_rate_per_mode; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.quick_connect_rates
    ADD CONSTRAINT chk_one_active_rate_per_mode EXCLUDE USING btree (mode WITH =) WHERE (((is_active = true) AND (deleted_at IS NULL)));


--
-- Name: consultant_payouts consultant_payouts_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.consultant_payouts
    ADD CONSTRAINT consultant_payouts_pkey PRIMARY KEY (payout_id);


--
-- Name: consultant_wallets consultant_wallets_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.consultant_wallets
    ADD CONSTRAINT consultant_wallets_pkey PRIMARY KEY (consultant_id);


--
-- Name: consultants consultants_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.consultants
    ADD CONSTRAINT consultants_pkey PRIMARY KEY (consultant_id);


--
-- Name: coupons coupons_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.coupons
    ADD CONSTRAINT coupons_pkey PRIMARY KEY (coupon_id);


--
-- Name: invoice_line_items invoice_line_items_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.invoice_line_items
    ADD CONSTRAINT invoice_line_items_pkey PRIMARY KEY (line_item_id);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (invoice_id);


--
-- Name: kombu_message kombu_message_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.kombu_message
    ADD CONSTRAINT kombu_message_pkey PRIMARY KEY (id);


--
-- Name: kombu_queue kombu_queue_name_key; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.kombu_queue
    ADD CONSTRAINT kombu_queue_name_key UNIQUE (name);


--
-- Name: kombu_queue kombu_queue_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.kombu_queue
    ADD CONSTRAINT kombu_queue_pkey PRIMARY KEY (id);


--
-- Name: payment_gateways payment_gateways_name_key; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_gateways
    ADD CONSTRAINT payment_gateways_name_key UNIQUE (name);


--
-- Name: payment_gateways payment_gateways_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_gateways
    ADD CONSTRAINT payment_gateways_pkey PRIMARY KEY (gateway_id);


--
-- Name: payment_orders payment_orders_gateway_order_id_key; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_orders
    ADD CONSTRAINT payment_orders_gateway_order_id_key UNIQUE (gateway_order_id);


--
-- Name: payment_orders payment_orders_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_orders
    ADD CONSTRAINT payment_orders_pkey PRIMARY KEY (payment_order_id);


--
-- Name: payment_transactions payment_transactions_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_transactions
    ADD CONSTRAINT payment_transactions_pkey PRIMARY KEY (payment_transaction_id);


--
-- Name: promotion_rules promotion_rules_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.promotion_rules
    ADD CONSTRAINT promotion_rules_pkey PRIMARY KEY (rule_id);


--
-- Name: quick_connect_rates quick_connect_rates_mode_is_active_key; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.quick_connect_rates
    ADD CONSTRAINT quick_connect_rates_mode_is_active_key UNIQUE (mode, is_active);


--
-- Name: quick_connect_rates quick_connect_rates_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.quick_connect_rates
    ADD CONSTRAINT quick_connect_rates_pkey PRIMARY KEY (rate_id);


--
-- Name: refund_audit refund_audit_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.refund_audit
    ADD CONSTRAINT refund_audit_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_name_key; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.tenants
    ADD CONSTRAINT tenants_name_key UNIQUE (name);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: payment_transactions uq_gateway_transaction_id_status; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_transactions
    ADD CONSTRAINT uq_gateway_transaction_id_status UNIQUE (gateway_transaction_id, status);


--
-- Name: consultants uq_tenant_consultant; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.consultants
    ADD CONSTRAINT uq_tenant_consultant UNIQUE (tenant_id, tenant_consultant_id);


--
-- Name: users uq_tenant_user; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.users
    ADD CONSTRAINT uq_tenant_user UNIQUE (tenant_id, tenant_user_id);


--
-- Name: wallet_orders uq_user_context_order; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_orders
    ADD CONSTRAINT uq_user_context_order UNIQUE (user_id, context_id);


--
-- Name: user_wallets user_wallets_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.user_wallets
    ADD CONSTRAINT user_wallets_pkey PRIMARY KEY (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: wallet_orders wallet_orders_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_orders
    ADD CONSTRAINT wallet_orders_pkey PRIMARY KEY (order_id);


--
-- Name: wallet_settings wallet_settings_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_settings
    ADD CONSTRAINT wallet_settings_pkey PRIMARY KEY (setting_id);


--
-- Name: wallet_transactions wallet_transactions_id_key; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_transactions
    ADD CONSTRAINT wallet_transactions_id_key UNIQUE (id);


--
-- Name: wallet_transactions wallet_transactions_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_transactions
    ADD CONSTRAINT wallet_transactions_pkey PRIMARY KEY (transaction_id);


--
-- Name: wallets wallets_pkey; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallets
    ADD CONSTRAINT wallets_pkey PRIMARY KEY (wallet_id);


--
-- Name: wallets wallets_user_id_key; Type: CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallets
    ADD CONSTRAINT wallets_user_id_key UNIQUE (user_id);


--
-- Name: ix_admin_admin_users_email; Type: INDEX; Schema: admin; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_admin_users_email ON admin.admin_users USING btree (email);


--
-- Name: ix_admin_admin_users_id; Type: INDEX; Schema: admin; Owner: postgres
--

CREATE INDEX ix_admin_admin_users_id ON admin.admin_users USING btree (id);


--
-- Name: ix_admin_admin_users_phone_number; Type: INDEX; Schema: admin; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_admin_users_phone_number ON admin.admin_users USING btree (phone_number);


--
-- Name: ix_admin_audit_logs_action; Type: INDEX; Schema: admin; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_action ON admin.audit_logs USING btree (action);


--
-- Name: ix_admin_audit_logs_admin_user_id; Type: INDEX; Schema: admin; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_admin_user_id ON admin.audit_logs USING btree (admin_user_id);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: admin; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON admin.audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_resource_id; Type: INDEX; Schema: admin; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_resource_id ON admin.audit_logs USING btree (resource_id);


--
-- Name: ix_admin_audit_logs_resource_type; Type: INDEX; Schema: admin; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_resource_type ON admin.audit_logs USING btree (resource_type);


--
-- Name: ix_admin_audit_logs_timestamp; Type: INDEX; Schema: admin; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_timestamp ON admin.audit_logs USING btree ("timestamp");


--
-- Name: idx_logged_actions_action; Type: INDEX; Schema: audit; Owner: postgres
--

CREATE INDEX idx_logged_actions_action ON audit.logged_actions USING btree (action);


--
-- Name: idx_logged_actions_new_data_gin; Type: INDEX; Schema: audit; Owner: postgres
--

CREATE INDEX idx_logged_actions_new_data_gin ON audit.logged_actions USING gin (new_data);


--
-- Name: idx_logged_actions_original_data_gin; Type: INDEX; Schema: audit; Owner: postgres
--

CREATE INDEX idx_logged_actions_original_data_gin ON audit.logged_actions USING gin (original_data);


--
-- Name: idx_logged_actions_schema_table_tstamp; Type: INDEX; Schema: audit; Owner: postgres
--

CREATE INDEX idx_logged_actions_schema_table_tstamp ON audit.logged_actions USING btree (schema_name, table_name, action_tstamp DESC);


--
-- Name: idx_logged_actions_tstamp_brin; Type: INDEX; Schema: audit; Owner: postgres
--

CREATE INDEX idx_logged_actions_tstamp_brin ON audit.logged_actions USING brin (action_tstamp) WITH (pages_per_range='128');


--
-- Name: logged_actions_action_idx; Type: INDEX; Schema: audit; Owner: postgres
--

CREATE INDEX logged_actions_action_idx ON audit.logged_actions USING btree (action);


--
-- Name: logged_actions_action_tstamp_idx; Type: INDEX; Schema: audit; Owner: postgres
--

CREATE INDEX logged_actions_action_tstamp_idx ON audit.logged_actions USING btree (action_tstamp);


--
-- Name: logged_actions_schema_table_idx; Type: INDEX; Schema: audit; Owner: postgres
--

CREATE INDEX logged_actions_schema_table_idx ON audit.logged_actions USING btree ((((schema_name || '.'::text) || table_name)));


--
-- Name: idx_auth_user_roles_auth_user_id; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_auth_user_roles_auth_user_id ON auth.auth_user_roles USING btree (auth_user_id);


--
-- Name: idx_auth_user_roles_role; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_auth_user_roles_role ON auth.auth_user_roles USING btree (role);


--
-- Name: idx_auth_users_deleted_at; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_auth_users_deleted_at ON auth.auth_users USING btree (deleted_at);


--
-- Name: idx_auth_users_is_test_user; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_auth_users_is_test_user ON auth.auth_users USING btree (is_test_user) WHERE (is_test_user = true);


--
-- Name: idx_auth_users_phone_number; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_auth_users_phone_number ON auth.auth_users USING btree (phone_number);


--
-- Name: idx_auth_users_phone_number_deleted_at; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE UNIQUE INDEX idx_auth_users_phone_number_deleted_at ON auth.auth_users USING btree (phone_number, deleted_at) WHERE (deleted_at IS NULL);


--
-- Name: INDEX idx_auth_users_phone_number_deleted_at; Type: COMMENT; Schema: auth; Owner: postgres
--

COMMENT ON INDEX auth.idx_auth_users_phone_number_deleted_at IS 'Ensures unique phone numbers among active (non-deleted) users';


--
-- Name: idx_login_activities_auth_user_id; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_login_activities_auth_user_id ON auth.login_activities USING btree (auth_user_id);


--
-- Name: idx_login_activities_session_id; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_login_activities_session_id ON auth.login_activities USING btree (session_id);


--
-- Name: idx_otp_attempts_auth_user_id; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_otp_attempts_auth_user_id ON auth.otp_attempts USING btree (auth_user_id);


--
-- Name: idx_otp_attempts_otp_request_id; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE UNIQUE INDEX idx_otp_attempts_otp_request_id ON auth.otp_attempts USING btree (otp_request_id);


--
-- Name: idx_user_devices_auth_user_id; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_user_devices_auth_user_id ON auth.user_devices USING btree (auth_user_id);


--
-- Name: idx_user_devices_device_id; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_user_devices_device_id ON auth.user_devices USING btree (device_id);


--
-- Name: INDEX idx_user_devices_device_id; Type: COMMENT; Schema: auth; Owner: postgres
--

COMMENT ON INDEX auth.idx_user_devices_device_id IS 'Non-unique index on device_id to allow device transfers between users while maintaining query performance.';


--
-- Name: idx_user_sessions_access_token; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_user_sessions_access_token ON auth.user_sessions USING btree (access_token);


--
-- Name: idx_user_sessions_auth_user_id; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_user_sessions_auth_user_id ON auth.user_sessions USING btree (auth_user_id);


--
-- Name: idx_user_sessions_device_id; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_user_sessions_device_id ON auth.user_sessions USING btree (device_id);


--
-- Name: idx_user_sessions_refresh_token; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE UNIQUE INDEX idx_user_sessions_refresh_token ON auth.user_sessions USING btree (refresh_token);


--
-- Name: idx_user_sessions_session_id; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE UNIQUE INDEX idx_user_sessions_session_id ON auth.user_sessions USING btree (session_id);


--
-- Name: feedback_consultation_id_unique; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE UNIQUE INDEX feedback_consultation_id_unique ON consultation.feedback USING btree (consultation_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_agora_session_consultation_id; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_agora_session_consultation_id ON consultation.agora_consultation_session USING btree (consultation_id);


--
-- Name: idx_agora_session_status; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_agora_session_status ON consultation.agora_consultation_session USING btree (status);


--
-- Name: idx_consultation_cloud_recording_resource_id; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_cloud_recording_resource_id ON consultation.consultation USING btree (cloud_recording_resource_id);


--
-- Name: idx_consultation_cloud_recording_session_id; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_cloud_recording_session_id ON consultation.consultation USING btree (cloud_recording_session_id);


--
-- Name: idx_consultation_customer_state; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_customer_state ON consultation.consultation USING btree (customer_id, state);


--
-- Name: idx_consultation_expires_at; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_expires_at ON consultation.consultation USING btree (expires_at) WHERE (expires_at IS NOT NULL);


--
-- Name: idx_consultation_free; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_free ON consultation.consultation USING btree (free);


--
-- Name: idx_consultation_guide_state; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_guide_state ON consultation.consultation USING btree (guide_id, state);


--
-- Name: idx_consultation_is_promotional; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_is_promotional ON consultation.consultation USING btree (is_promotional_consultation);


--
-- Name: idx_consultation_is_refundable; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_is_refundable ON consultation.consultation USING btree (is_refundable) WHERE ((is_refundable = true) AND (state = 'completed'::consultation.consultation_state));


--
-- Name: idx_consultation_is_refunded; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_is_refunded ON consultation.consultation USING btree (is_refunded) WHERE (is_refunded = true);


--
-- Name: idx_consultation_offer_applied; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_offer_applied ON consultation.consultation USING btree (offer_applied);


--
-- Name: idx_consultation_offer_id; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_offer_id ON consultation.consultation USING btree (offer_id);


--
-- Name: idx_consultation_offer_reservation_id; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_offer_reservation_id ON consultation.consultation USING btree (offer_reservation_id);


--
-- Name: idx_consultation_promotional; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_promotional ON consultation.consultation USING btree (promotional);


--
-- Name: idx_consultation_requested_by; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_requested_by ON consultation.consultation USING btree (requested_by);


--
-- Name: idx_consultation_state; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_consultation_state ON consultation.consultation USING btree (state);


--
-- Name: idx_feedback_consultation_id; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_feedback_consultation_id ON consultation.feedback USING btree (consultation_id);


--
-- Name: idx_feedback_created_at; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_feedback_created_at ON consultation.feedback USING btree (created_at);


--
-- Name: idx_feedback_rating; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_feedback_rating ON consultation.feedback USING btree (rating);


--
-- Name: idx_feedback_reports_customers; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_feedback_reports_customers ON consultation.feedback USING gin (((reports -> 'customers'::text)));


--
-- Name: idx_feedback_reports_guides; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_feedback_reports_guides ON consultation.feedback USING gin (((reports -> 'guides'::text)));


--
-- Name: idx_feedback_status; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_feedback_status ON consultation.feedback USING btree (status);


--
-- Name: idx_quality_metrics_consultation_id; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_quality_metrics_consultation_id ON consultation.consultation_quality_metrics USING btree (consultation_id);


--
-- Name: idx_quality_metrics_created_at; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_quality_metrics_created_at ON consultation.consultation_quality_metrics USING btree (created_at);


--
-- Name: idx_quality_metrics_guide_id; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_quality_metrics_guide_id ON consultation.consultation_quality_metrics USING btree (guide_id);


--
-- Name: idx_quality_metrics_short_consultation; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_quality_metrics_short_consultation ON consultation.consultation_quality_metrics USING btree (is_short_consultation);


--
-- Name: idx_webhook_event_type; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_webhook_event_type ON consultation.agora_webhook_events USING btree (event_type);


--
-- Name: idx_webhook_session_id; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE INDEX idx_webhook_session_id ON consultation.agora_webhook_events USING btree (consultation_session_id);


--
-- Name: uq_active_consultation_pair; Type: INDEX; Schema: consultation; Owner: postgres
--

CREATE UNIQUE INDEX uq_active_consultation_pair ON consultation.consultation USING btree (guide_id, customer_id) WHERE (state = 'in_progress'::consultation.consultation_state);


--
-- Name: idx_address_deleted_at; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE INDEX idx_address_deleted_at ON customers.address USING btree (deleted_at);


--
-- Name: idx_customer_address_deleted_at; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE INDEX idx_customer_address_deleted_at ON customers.customer_address USING btree (deleted_at);


--
-- Name: idx_customer_deleted_at; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE INDEX idx_customer_deleted_at ON customers.customer USING btree (deleted_at);


--
-- Name: idx_customer_phone; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE INDEX idx_customer_phone ON customers.customer USING btree (country_code, phone_number);


--
-- Name: idx_customer_phone_active; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE UNIQUE INDEX idx_customer_phone_active ON customers.customer USING btree (country_code, phone_number) WHERE (deleted_at IS NULL);


--
-- Name: INDEX idx_customer_phone_active; Type: COMMENT; Schema: customers; Owner: postgres
--

COMMENT ON INDEX customers.idx_customer_phone_active IS 'Allows phone number reuse after account deletion';


--
-- Name: idx_customer_primary_address; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE UNIQUE INDEX idx_customer_primary_address ON customers.customer_address USING btree (customer_id) WHERE (is_primary = true);


--
-- Name: idx_customer_primary_profile; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE UNIQUE INDEX idx_customer_primary_profile ON customers.customer_profile USING btree (customer_id) WHERE (is_primary = true);


--
-- Name: idx_customer_profile_deleted_at; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE INDEX idx_customer_profile_deleted_at ON customers.customer_profile USING btree (deleted_at);


--
-- Name: idx_customer_wallet_user_id; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE INDEX idx_customer_wallet_user_id ON customers.customer USING btree (wallet_user_id);


--
-- Name: idx_customer_x_auth_id_active; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE UNIQUE INDEX idx_customer_x_auth_id_active ON customers.customer USING btree (x_auth_id) WHERE ((x_auth_id IS NOT NULL) AND (deleted_at IS NULL));


--
-- Name: INDEX idx_customer_x_auth_id_active; Type: COMMENT; Schema: customers; Owner: postgres
--

COMMENT ON INDEX customers.idx_customer_x_auth_id_active IS 'Allows x_auth_id reuse after account deletion';


--
-- Name: idx_customeraddress_address_id; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE INDEX idx_customeraddress_address_id ON customers.customer_address USING btree (address_id);


--
-- Name: idx_customeraddress_customer_id; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE INDEX idx_customeraddress_customer_id ON customers.customer_address USING btree (customer_id);


--
-- Name: idx_customerprofile_customer_id; Type: INDEX; Schema: customers; Owner: postgres
--

CREATE INDEX idx_customerprofile_customer_id ON customers.customer_profile USING btree (customer_id);


--
-- Name: guide_profile_email_composite_unique; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX guide_profile_email_composite_unique ON guide.guide_profile USING btree (email, is_deleted, deleted_at);


--
-- Name: INDEX guide_profile_email_composite_unique; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON INDEX guide.guide_profile_email_composite_unique IS 'Composite unique constraint allowing email reuse after account deletion';


--
-- Name: guide_profile_email_unique_active; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX guide_profile_email_unique_active ON guide.guide_profile USING btree (email) WHERE (deleted_at IS NULL);


--
-- Name: guide_profile_phone_number_composite_unique; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX guide_profile_phone_number_composite_unique ON guide.guide_profile USING btree (phone_number, is_deleted, deleted_at);


--
-- Name: INDEX guide_profile_phone_number_composite_unique; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON INDEX guide.guide_profile_phone_number_composite_unique IS 'Composite unique constraint allowing phone number reuse after account deletion';


--
-- Name: guide_profile_phone_number_unique_active; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX guide_profile_phone_number_unique_active ON guide.guide_profile USING btree (phone_number) WHERE (deleted_at IS NULL);


--
-- Name: guide_profile_referral_code_unique_active; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX guide_profile_referral_code_unique_active ON guide.guide_profile USING btree (referral_code) WHERE ((deleted_at IS NULL) AND (referral_code IS NOT NULL));


--
-- Name: guide_profile_video_channel_unique_active; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX guide_profile_video_channel_unique_active ON guide.guide_profile USING btree (video_channel_name) WHERE ((deleted_at IS NULL) AND (video_channel_name IS NOT NULL));


--
-- Name: guide_profile_voice_channel_unique_active; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX guide_profile_voice_channel_unique_active ON guide.guide_profile USING btree (voice_channel_name) WHERE ((deleted_at IS NULL) AND (voice_channel_name IS NOT NULL));


--
-- Name: guide_profile_x_auth_id_unique_active; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX guide_profile_x_auth_id_unique_active ON guide.guide_profile USING btree (x_auth_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_address_default; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX idx_address_default ON guide.addresses USING btree (guide_id) WHERE (is_default AND (deleted_at IS NULL));


--
-- Name: idx_bank_account_default; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX idx_bank_account_default ON guide.bank_account USING btree (guide_id) WHERE (is_default AND (deleted_at IS NULL));


--
-- Name: idx_bank_account_number; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_bank_account_number ON guide.bank_account USING btree (account_number);


--
-- Name: idx_guide_availability_ranking; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_guide_availability_ranking ON guide.guide_profile USING btree (availability_state, ranking_score DESC) WHERE (deleted_at IS NULL);


--
-- Name: INDEX idx_guide_availability_ranking; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON INDEX guide.idx_guide_availability_ranking IS 'Composite index to optimize guide listing queries that sort by availability state first, then ranking score';


--
-- Name: idx_guide_availability_state; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_guide_availability_state ON guide.guide_profile USING btree (availability_state) WHERE (deleted_at IS NULL);


--
-- Name: idx_guide_chat_enabled; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_guide_chat_enabled ON guide.guide_profile USING btree (updated_at DESC) WHERE ((chat_enabled = true) AND (deleted_at IS NULL));


--
-- Name: idx_guide_is_celebrity; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_guide_is_celebrity ON guide.guide_profile USING gin (properties jsonb_path_ops) WHERE ((properties ->> 'is_celebrity'::text) = 'true'::text);


--
-- Name: idx_guide_is_test_guide; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_guide_is_test_guide ON guide.guide_profile USING btree (((properties ->> 'is_test_guide'::text)));


--
-- Name: idx_guide_profile_audit_deleted_at; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_guide_profile_audit_deleted_at ON guide.guide_profile_audit USING btree (deleted_at);


--
-- Name: idx_guide_profile_tier; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_guide_profile_tier ON guide.guide_profile USING btree (tier);


--
-- Name: idx_guide_ranking_score; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_guide_ranking_score ON guide.guide_profile USING btree (ranking_score DESC) WHERE (deleted_at IS NULL);


--
-- Name: idx_guide_skills_skill; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_guide_skills_skill ON guide.guide_skills USING btree (skill_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_guide_voice_enabled; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_guide_voice_enabled ON guide.guide_profile USING btree (updated_at DESC) WHERE ((voice_enabled = true) AND (deleted_at IS NULL));


--
-- Name: idx_profile_state; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_profile_state ON guide.guide_profile USING btree (onboarding_state);


--
-- Name: idx_saved_messages_guide_created; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_saved_messages_guide_created ON guide.saved_messages USING btree (guide_id, created_at DESC) WHERE (deleted_at IS NULL);


--
-- Name: idx_saved_messages_guide_id; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_saved_messages_guide_id ON guide.saved_messages USING btree (guide_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_verif_agreement_live; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX idx_verif_agreement_live ON guide.verification USING btree (guide_id, agreement_id) WHERE ((target_type = 'AGREEMENT'::guide.verification_target_enum) AND (deleted_at IS NULL));


--
-- Name: idx_verif_bank_live; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX idx_verif_bank_live ON guide.verification USING btree (guide_id, bank_account_id) WHERE ((target_type = 'BANK_ACCOUNT'::guide.verification_target_enum) AND (deleted_at IS NULL));


--
-- Name: idx_verif_kyc_live; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX idx_verif_kyc_live ON guide.verification USING btree (guide_id, kyc_document_id) WHERE ((target_type = 'KYC_DOCUMENT'::guide.verification_target_enum) AND (deleted_at IS NULL));


--
-- Name: idx_verification_audit_log_deleted_at; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_verification_audit_log_deleted_at ON guide.verification_audit_log USING btree (deleted_at);


--
-- Name: idx_verification_guide_status; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE INDEX idx_verification_guide_status ON guide.verification USING btree (guide_id, target_type, status) WHERE (deleted_at IS NULL);


--
-- Name: idx_video_channel_unique; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX idx_video_channel_unique ON guide.guide_profile USING btree (video_channel_name) WHERE (video_channel_name IS NOT NULL);


--
-- Name: idx_voice_channel_unique; Type: INDEX; Schema: guide; Owner: postgres
--

CREATE UNIQUE INDEX idx_voice_channel_unique ON guide.guide_profile USING btree (voice_channel_name) WHERE (voice_channel_name IS NOT NULL);


--
-- Name: idx_leads_created_at; Type: INDEX; Schema: marketing; Owner: postgres
--

CREATE INDEX idx_leads_created_at ON marketing.leads USING btree (created_at);


--
-- Name: idx_leads_info; Type: INDEX; Schema: marketing; Owner: postgres
--

CREATE INDEX idx_leads_info ON marketing.leads USING gin (info);


--
-- Name: idx_leads_phone; Type: INDEX; Schema: marketing; Owner: postgres
--

CREATE INDEX idx_leads_phone ON marketing.leads USING btree (phone);


--
-- Name: idx_leads_source; Type: INDEX; Schema: marketing; Owner: postgres
--

CREATE INDEX idx_leads_source ON marketing.leads USING btree (source);


--
-- Name: idx_client_events_analytics; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_client_events_analytics ON notifications.client_events USING btree (created_at DESC, event_type, platform);


--
-- Name: idx_client_events_device_id; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_client_events_device_id ON notifications.client_events USING btree (device_id);


--
-- Name: idx_client_events_device_timestamp; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_client_events_device_timestamp ON notifications.client_events USING btree (device_id, "timestamp" DESC);


--
-- Name: idx_client_events_event_id; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE UNIQUE INDEX idx_client_events_event_id ON notifications.client_events USING btree (event_id);


--
-- Name: idx_client_events_event_type_platform; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_client_events_event_type_platform ON notifications.client_events USING btree (event_type, platform, created_at DESC);


--
-- Name: idx_client_events_platform; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_client_events_platform ON notifications.client_events USING btree (platform);


--
-- Name: idx_client_events_priority; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_client_events_priority ON notifications.client_events USING btree (priority);


--
-- Name: idx_client_events_session_id; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_client_events_session_id ON notifications.client_events USING btree (session_id);


--
-- Name: idx_client_events_timestamp; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_client_events_timestamp ON notifications.client_events USING btree ("timestamp");


--
-- Name: idx_client_events_user_created; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_client_events_user_created ON notifications.client_events USING btree (user_id, created_at DESC);


--
-- Name: idx_delivery_attempts_channel; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_delivery_attempts_channel ON notifications.delivery_attempts USING btree (channel);


--
-- Name: idx_delivery_attempts_created_at; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_delivery_attempts_created_at ON notifications.delivery_attempts USING btree (created_at);


--
-- Name: idx_delivery_attempts_event_channel; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_delivery_attempts_event_channel ON notifications.delivery_attempts USING btree (event_id, channel);


--
-- Name: idx_delivery_attempts_event_id; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_delivery_attempts_event_id ON notifications.delivery_attempts USING btree (event_id);


--
-- Name: idx_delivery_attempts_next_retry_at; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_delivery_attempts_next_retry_at ON notifications.delivery_attempts USING btree (next_retry_at);


--
-- Name: idx_delivery_attempts_retry; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_delivery_attempts_retry ON notifications.delivery_attempts USING btree (next_retry_at) WHERE ((status = 'failed'::text) AND (next_retry_at IS NOT NULL));


--
-- Name: idx_delivery_attempts_status; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_delivery_attempts_status ON notifications.delivery_attempts USING btree (status);


--
-- Name: idx_escalation_rules_event_priority; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_escalation_rules_event_priority ON notifications.escalation_rules USING btree (event_type, priority) WHERE (is_active = true);


--
-- Name: idx_escalation_rules_event_type; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_escalation_rules_event_type ON notifications.escalation_rules USING btree (event_type);


--
-- Name: idx_escalation_rules_priority; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_escalation_rules_priority ON notifications.escalation_rules USING btree (priority);


--
-- Name: idx_event_type_user; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_event_type_user ON notifications.client_events USING btree (event_type, user_id);


--
-- Name: idx_notifications_channel; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_notifications_channel ON notifications.notifications USING btree (channel);


--
-- Name: idx_notifications_event_type; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_notifications_event_type ON notifications.notifications USING btree (event_type);


--
-- Name: idx_notifications_is_read; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_notifications_is_read ON notifications.notifications USING btree (is_read);


--
-- Name: idx_notifications_priority; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_notifications_priority ON notifications.notifications USING btree (priority);


--
-- Name: idx_notifications_scheduled_at; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_notifications_scheduled_at ON notifications.notifications USING btree (scheduled_at);


--
-- Name: idx_notifications_scheduled_pending; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_notifications_scheduled_pending ON notifications.notifications USING btree (scheduled_at) WHERE ((scheduled_at IS NOT NULL) AND (delivered_at IS NULL));


--
-- Name: idx_notifications_target_type; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_notifications_target_type ON notifications.notifications USING btree (target_type);


--
-- Name: idx_notifications_user_created_priority; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_notifications_user_created_priority ON notifications.notifications USING btree (auth_user_id, created_at DESC, priority);


--
-- Name: idx_user_created; Type: INDEX; Schema: notifications; Owner: postgres
--

CREATE INDEX idx_user_created ON notifications.notifications USING btree (auth_user_id, created_at);


--
-- Name: idx_consultant_rates_active_window; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consultant_rates_active_window ON offers.consultant_rates USING btree (is_active, valid_from, valid_to);


--
-- Name: idx_consultant_rates_consultant; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consultant_rates_consultant ON offers.consultant_rates USING btree (consultant_id);


--
-- Name: idx_consultant_rates_deleted_at; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consultant_rates_deleted_at ON offers.consultant_rates USING btree (deleted_at);


--
-- Name: idx_consumptions_deleted_at; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consumptions_deleted_at ON offers.offer_consumptions USING btree (deleted_at);


--
-- Name: idx_consumptions_offer_id; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consumptions_offer_id ON offers.offer_consumptions USING btree (offer_id);


--
-- Name: idx_consumptions_reservation_id; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consumptions_reservation_id ON offers.offer_consumptions USING btree (reservation_id);


--
-- Name: idx_consumptions_status; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consumptions_status ON offers.offer_consumptions USING btree (consumption_status);


--
-- Name: idx_consumptions_user_id; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consumptions_user_id ON offers.offer_consumptions USING btree (user_id);


--
-- Name: idx_consumptions_user_status; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consumptions_user_status ON offers.offer_consumptions USING btree (user_id, consumption_status);


--
-- Name: idx_consumptions_voucher_instance; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consumptions_voucher_instance ON offers.offer_consumptions USING btree (voucher_instance_id) WHERE (voucher_instance_id IS NOT NULL);


--
-- Name: idx_consumptions_wallet_transaction; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_consumptions_wallet_transaction ON offers.offer_consumptions USING btree (wallet_transaction_id);


--
-- Name: idx_first_time; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_first_time ON offers.user_behavior_metrics USING btree (is_first_time_user);


--
-- Name: idx_milestone_offer; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_milestone_offer ON offers.user_milestone_progress USING btree (offer_id);


--
-- Name: idx_milestone_progress_deleted_at; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_milestone_progress_deleted_at ON offers.user_milestone_progress USING btree (deleted_at);


--
-- Name: idx_milestone_reached; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_milestone_reached ON offers.user_milestone_progress USING btree (milestone_reached, voucher_distributed);


--
-- Name: idx_milestone_triggered_at; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_milestone_triggered_at ON offers.user_milestone_progress USING btree (triggered_at);


--
-- Name: idx_milestone_user; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_milestone_user ON offers.user_milestone_progress USING btree (user_id);


--
-- Name: idx_offer_campaigns_dates; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_campaigns_dates ON offers.offer_campaigns USING btree (start_date, end_date);


--
-- Name: idx_offer_campaigns_offer_id; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_campaigns_offer_id ON offers.offer_campaigns USING btree (offer_id);


--
-- Name: idx_offer_campaigns_status; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_campaigns_status ON offers.offer_campaigns USING btree (status);


--
-- Name: idx_offer_consumptions_wallet_order_id; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_consumptions_wallet_order_id ON offers.offer_consumptions USING btree (wallet_order_id) WHERE (wallet_order_id IS NOT NULL);


--
-- Name: idx_offer_definitions_active; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_definitions_active ON offers.offer_definitions USING btree (is_active);


--
-- Name: idx_offer_definitions_all_consultant; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_definitions_all_consultant ON offers.offer_definitions USING btree (all_consultant_applicable);


--
-- Name: idx_offer_definitions_applicable_consultants; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_definitions_applicable_consultants ON offers.offer_definitions USING gin (applicable_consultants);


--
-- Name: idx_offer_definitions_category; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_definitions_category ON offers.offer_definitions USING btree (offer_category);


--
-- Name: idx_offer_definitions_deleted_at; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_definitions_deleted_at ON offers.offer_definitions USING btree (deleted_at);


--
-- Name: idx_offer_definitions_target_guide_tiers; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_definitions_target_guide_tiers ON offers.offer_definitions USING gin (target_guide_tiers);


--
-- Name: idx_offer_definitions_type; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_definitions_type ON offers.offer_definitions USING btree (offer_type);


--
-- Name: idx_offer_definitions_validity; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_definitions_validity ON offers.offer_definitions USING btree (valid_from, valid_to);


--
-- Name: idx_offer_reservations_wallet_order_id; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_offer_reservations_wallet_order_id ON offers.offer_reservations USING btree (wallet_order_id) WHERE (wallet_order_id IS NOT NULL);


--
-- Name: idx_registration_source; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_registration_source ON offers.user_behavior_metrics USING btree (registration_source);


--
-- Name: idx_reservation_active_unique; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE UNIQUE INDEX idx_reservation_active_unique ON offers.offer_reservations USING btree (offer_id, user_id) WHERE ((reservation_status)::text = 'ACTIVE'::text);


--
-- Name: idx_reservations_consultation; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_reservations_consultation ON offers.offer_reservations USING btree (consultation_id) WHERE (consultation_id IS NOT NULL);


--
-- Name: idx_reservations_deleted_at; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_reservations_deleted_at ON offers.offer_reservations USING btree (deleted_at);


--
-- Name: idx_reservations_expires_at; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_reservations_expires_at ON offers.offer_reservations USING btree (expires_at);


--
-- Name: idx_reservations_offer_id; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_reservations_offer_id ON offers.offer_reservations USING btree (offer_id);


--
-- Name: idx_reservations_payment_order; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_reservations_payment_order ON offers.offer_reservations USING btree (payment_order_id);


--
-- Name: idx_reservations_status; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_reservations_status ON offers.offer_reservations USING btree (reservation_status);


--
-- Name: idx_reservations_user_id; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_reservations_user_id ON offers.offer_reservations USING btree (user_id);


--
-- Name: idx_reservations_user_status; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_reservations_user_status ON offers.offer_reservations USING btree (user_id, reservation_status);


--
-- Name: idx_user_metrics_last_activity; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_user_metrics_last_activity ON offers.user_behavior_metrics USING btree (last_activity_at);


--
-- Name: idx_user_metrics_last_consultation; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_user_metrics_last_consultation ON offers.user_behavior_metrics USING btree (last_consultation_at);


--
-- Name: idx_user_metrics_last_offer; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_user_metrics_last_offer ON offers.user_behavior_metrics USING btree (last_offer_used_at);


--
-- Name: idx_user_metrics_service_type; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_user_metrics_service_type ON offers.user_behavior_metrics USING btree (preferred_service_type);


--
-- Name: idx_user_segment; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_user_segment ON offers.user_behavior_metrics USING btree (user_segment);


--
-- Name: idx_user_segments_customer; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_user_segments_customer ON offers.user_segments USING btree (customer_id);


--
-- Name: idx_user_segments_type; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_user_segments_type ON offers.user_segments USING btree (segment_type);


--
-- Name: idx_volume_bonus_date; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_volume_bonus_date ON offers.volume_bonus_tracking USING btree (consultation_date);


--
-- Name: idx_volume_bonus_offer; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_volume_bonus_offer ON offers.volume_bonus_tracking USING btree (offer_id);


--
-- Name: idx_volume_bonus_user; Type: INDEX; Schema: offers; Owner: postgres
--

CREATE INDEX idx_volume_bonus_user ON offers.volume_bonus_tracking USING btree (user_id);


--
-- Name: idx_consultant_wallets_phone_unique; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE UNIQUE INDEX idx_consultant_wallets_phone_unique ON wallet.consultant_wallets USING btree (phone_number) WHERE (deleted_at IS NULL);


--
-- Name: idx_consultants_phone_unique; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE UNIQUE INDEX idx_consultants_phone_unique ON wallet.consultants USING btree (phone_number);


--
-- Name: idx_payment_order_id_success; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE UNIQUE INDEX idx_payment_order_id_success ON wallet.payment_transactions USING btree (payment_order_id) WHERE ((status)::text = 'SUCCESS'::text);


--
-- Name: idx_payment_orders_external_gateway; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_payment_orders_external_gateway ON wallet.payment_orders USING btree (external_gateway) WHERE (external_gateway IS NOT NULL);


--
-- Name: idx_payment_orders_external_reference_unique; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE UNIQUE INDEX idx_payment_orders_external_reference_unique ON wallet.payment_orders USING btree (external_reference_id) WHERE (external_reference_id IS NOT NULL);


--
-- Name: idx_payment_orders_is_external; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_payment_orders_is_external ON wallet.payment_orders USING btree (is_external_payment) WHERE (is_external_payment = true);


--
-- Name: idx_quick_connect_rates_mode_active; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_quick_connect_rates_mode_active ON wallet.quick_connect_rates USING btree (mode, is_active) WHERE (deleted_at IS NULL);


--
-- Name: idx_refund_audit_consultation; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_refund_audit_consultation ON wallet.refund_audit USING btree (consultation_id);


--
-- Name: idx_refund_audit_created_at; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_refund_audit_created_at ON wallet.refund_audit USING btree (created_at);


--
-- Name: idx_refund_audit_customer; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_refund_audit_customer ON wallet.refund_audit USING btree (customer_wallet_user_id);


--
-- Name: idx_refund_audit_failed; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_refund_audit_failed ON wallet.refund_audit USING btree (refund_status, consultation_id) WHERE (refund_status = 'FAILED'::wallet.refund_status);


--
-- Name: idx_refund_audit_status; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_refund_audit_status ON wallet.refund_audit USING btree (refund_status);


--
-- Name: idx_unique_active_setting; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE UNIQUE INDEX idx_unique_active_setting ON wallet.wallet_settings USING btree (setting_key) WHERE (is_active = true);


--
-- Name: idx_user_wallets_phone_unique; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE UNIQUE INDEX idx_user_wallets_phone_unique ON wallet.user_wallets USING btree (phone_number) WHERE (deleted_at IS NULL);


--
-- Name: idx_users_phone_unique; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE UNIQUE INDEX idx_users_phone_unique ON wallet.users USING btree (phone_number);


--
-- Name: idx_wallet_orders_context_id; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_wallet_orders_context_id ON wallet.wallet_orders USING btree (context_id);


--
-- Name: idx_wallet_orders_is_refunded; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_wallet_orders_is_refunded ON wallet.wallet_orders USING btree (is_refunded) WHERE (is_refunded = true);


--
-- Name: idx_wallet_transactions_user_id; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_wallet_transactions_user_id ON wallet.wallet_transactions USING btree (user_id);


--
-- Name: idx_walletorder_consultant_id; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_walletorder_consultant_id ON wallet.wallet_orders USING btree (consultant_id);


--
-- Name: idx_walletorder_free; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_walletorder_free ON wallet.wallet_orders USING btree (free);


--
-- Name: idx_walletorder_promotional; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_walletorder_promotional ON wallet.wallet_orders USING btree (promotional);


--
-- Name: idx_walletorder_status; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_walletorder_status ON wallet.wallet_orders USING btree (status);


--
-- Name: idx_walletorder_user_id; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX idx_walletorder_user_id ON wallet.wallet_orders USING btree (user_id);


--
-- Name: ix_kombu_message_timestamp; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX ix_kombu_message_timestamp ON wallet.kombu_message USING btree ("timestamp");


--
-- Name: ix_kombu_message_timestamp_id; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX ix_kombu_message_timestamp_id ON wallet.kombu_message USING btree ("timestamp", id);


--
-- Name: ix_kombu_message_visible; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX ix_kombu_message_visible ON wallet.kombu_message USING btree (visible);


--
-- Name: ix_wallet_coupons_coupon_code; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE UNIQUE INDEX ix_wallet_coupons_coupon_code ON wallet.coupons USING btree (coupon_code);


--
-- Name: ix_wallet_payment_orders_task_id; Type: INDEX; Schema: wallet; Owner: postgres
--

CREATE INDEX ix_wallet_payment_orders_task_id ON wallet.payment_orders USING btree (task_id);


--
-- Name: agora_consultation_session agora_consultation_session_audit; Type: TRIGGER; Schema: consultation; Owner: postgres
--

CREATE TRIGGER agora_consultation_session_audit AFTER INSERT OR DELETE OR UPDATE ON consultation.agora_consultation_session FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: agora_webhook_events agora_webhook_events_audit; Type: TRIGGER; Schema: consultation; Owner: postgres
--

CREATE TRIGGER agora_webhook_events_audit AFTER INSERT OR DELETE OR UPDATE ON consultation.agora_webhook_events FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: consultation consultation_audit; Type: TRIGGER; Schema: consultation; Owner: postgres
--

CREATE TRIGGER consultation_audit AFTER INSERT OR DELETE OR UPDATE ON consultation.consultation FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: feedback feedback_audit; Type: TRIGGER; Schema: consultation; Owner: postgres
--

CREATE TRIGGER feedback_audit AFTER INSERT OR DELETE OR UPDATE ON consultation.feedback FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: feedback_comments_by_guide feedback_comments_by_guide_audit; Type: TRIGGER; Schema: consultation; Owner: postgres
--

CREATE TRIGGER feedback_comments_by_guide_audit AFTER INSERT OR DELETE OR UPDATE ON consultation.feedback_comments_by_guide FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: consultation trig_increment_consultation_version; Type: TRIGGER; Schema: consultation; Owner: postgres
--

CREATE TRIGGER trig_increment_consultation_version BEFORE UPDATE ON consultation.consultation FOR EACH ROW EXECUTE FUNCTION consultation.increment_version();


--
-- Name: agora_consultation_session trig_update_session_duration; Type: TRIGGER; Schema: consultation; Owner: postgres
--

CREATE TRIGGER trig_update_session_duration BEFORE UPDATE ON consultation.agora_consultation_session FOR EACH ROW EXECUTE FUNCTION consultation.update_session_duration();


--
-- Name: address address_audit; Type: TRIGGER; Schema: customers; Owner: postgres
--

CREATE TRIGGER address_audit AFTER INSERT OR DELETE OR UPDATE ON customers.address FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: customer_address customer_address_audit; Type: TRIGGER; Schema: customers; Owner: postgres
--

CREATE TRIGGER customer_address_audit AFTER INSERT OR DELETE OR UPDATE ON customers.customer_address FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: customer customer_audit; Type: TRIGGER; Schema: customers; Owner: postgres
--

CREATE TRIGGER customer_audit AFTER INSERT OR DELETE OR UPDATE ON customers.customer FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: customer_profile customer_profile_audit; Type: TRIGGER; Schema: customers; Owner: postgres
--

CREATE TRIGGER customer_profile_audit AFTER INSERT OR DELETE OR UPDATE ON customers.customer_profile FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: addresses addresses_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER addresses_audit AFTER INSERT OR DELETE OR UPDATE ON guide.addresses FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: agreement agreement_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER agreement_audit AFTER INSERT OR DELETE OR UPDATE ON guide.agreement FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: bank_account bank_account_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER bank_account_audit AFTER INSERT OR DELETE OR UPDATE ON guide.bank_account FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: guide_languages guide_languages_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER guide_languages_audit AFTER INSERT OR DELETE OR UPDATE ON guide.guide_languages FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: guide_profile guide_profile_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER guide_profile_audit AFTER INSERT OR DELETE OR UPDATE ON guide.guide_profile FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: guide_profile_audit guide_profile_audit_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER guide_profile_audit_audit AFTER INSERT OR DELETE OR UPDATE ON guide.guide_profile_audit FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: guide_skills guide_skills_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER guide_skills_audit AFTER INSERT OR DELETE OR UPDATE ON guide.guide_skills FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: kyc_document kyc_document_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER kyc_document_audit AFTER INSERT OR DELETE OR UPDATE ON guide.kyc_document FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: languages languages_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER languages_audit AFTER INSERT OR DELETE OR UPDATE ON guide.languages FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: media media_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER media_audit AFTER INSERT OR DELETE OR UPDATE ON guide.media FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: skills skills_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER skills_audit AFTER INSERT OR DELETE OR UPDATE ON guide.skills FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: addresses trg_addresses_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_addresses_set_updated_at BEFORE UPDATE ON guide.addresses FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: agreement trg_agreement_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_agreement_set_updated_at BEFORE UPDATE ON guide.agreement FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: bank_account trg_bank_account_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_bank_account_set_updated_at BEFORE UPDATE ON guide.bank_account FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: guide_profile trg_guide_profile_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_guide_profile_set_updated_at BEFORE UPDATE ON guide.guide_profile FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: kyc_document trg_kyc_document_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_kyc_document_set_updated_at BEFORE UPDATE ON guide.kyc_document FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: languages trg_languages_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_languages_set_updated_at BEFORE UPDATE ON guide.languages FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: media trg_media_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_media_set_updated_at BEFORE UPDATE ON guide.media FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: saved_messages trg_saved_messages_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_saved_messages_set_updated_at BEFORE UPDATE ON guide.saved_messages FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: skills trg_skills_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_skills_set_updated_at BEFORE UPDATE ON guide.skills FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: verification_audit_log trg_verification_audit_log_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_verification_audit_log_set_updated_at BEFORE UPDATE ON guide.verification_audit_log FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: verification trg_verification_set_updated_at; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER trg_verification_set_updated_at BEFORE UPDATE ON guide.verification FOR EACH ROW EXECUTE FUNCTION guide.set_updated_at();


--
-- Name: verification verification_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER verification_audit AFTER INSERT OR DELETE OR UPDATE ON guide.verification FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: verification_audit_log verification_audit_log_audit; Type: TRIGGER; Schema: guide; Owner: postgres
--

CREATE TRIGGER verification_audit_log_audit AFTER INSERT OR DELETE OR UPDATE ON guide.verification_audit_log FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: client_events update_client_events_updated_at; Type: TRIGGER; Schema: notifications; Owner: postgres
--

CREATE TRIGGER update_client_events_updated_at BEFORE UPDATE ON notifications.client_events FOR EACH ROW EXECUTE FUNCTION notifications.update_updated_at_column();


--
-- Name: delivery_attempts update_delivery_attempts_updated_at; Type: TRIGGER; Schema: notifications; Owner: postgres
--

CREATE TRIGGER update_delivery_attempts_updated_at BEFORE UPDATE ON notifications.delivery_attempts FOR EACH ROW EXECUTE FUNCTION notifications.update_updated_at_column();


--
-- Name: escalation_rules update_escalation_rules_updated_at; Type: TRIGGER; Schema: notifications; Owner: postgres
--

CREATE TRIGGER update_escalation_rules_updated_at BEFORE UPDATE ON notifications.escalation_rules FOR EACH ROW EXECUTE FUNCTION notifications.update_updated_at_column();


--
-- Name: notifications update_notifications_updated_at; Type: TRIGGER; Schema: notifications; Owner: postgres
--

CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON notifications.notifications FOR EACH ROW EXECUTE FUNCTION notifications.update_updated_at_column();


--
-- Name: offer_consumptions set_offer_consumption_timestamp; Type: TRIGGER; Schema: offers; Owner: postgres
--

CREATE TRIGGER set_offer_consumption_timestamp BEFORE INSERT ON offers.offer_consumptions FOR EACH ROW EXECUTE FUNCTION offers.set_consumption_timestamp();


--
-- Name: consultant_rates trg_update_consultant_rates_updated_at; Type: TRIGGER; Schema: offers; Owner: postgres
--

CREATE TRIGGER trg_update_consultant_rates_updated_at BEFORE UPDATE ON offers.consultant_rates FOR EACH ROW EXECUTE FUNCTION offers.update_updated_at_column();


--
-- Name: user_milestone_progress update_milestone_updated_at_trigger; Type: TRIGGER; Schema: offers; Owner: postgres
--

CREATE TRIGGER update_milestone_updated_at_trigger BEFORE UPDATE ON offers.user_milestone_progress FOR EACH ROW EXECUTE FUNCTION offers.update_updated_at_column();


--
-- Name: offer_consumptions update_offer_consumptions_updated_at; Type: TRIGGER; Schema: offers; Owner: postgres
--

CREATE TRIGGER update_offer_consumptions_updated_at BEFORE UPDATE ON offers.offer_consumptions FOR EACH ROW EXECUTE FUNCTION offers.update_updated_at_column();


--
-- Name: offer_definitions update_offer_definitions_updated_at; Type: TRIGGER; Schema: offers; Owner: postgres
--

CREATE TRIGGER update_offer_definitions_updated_at BEFORE UPDATE ON offers.offer_definitions FOR EACH ROW EXECUTE FUNCTION offers.update_updated_at_column();


--
-- Name: offer_reservations update_offer_reservations_updated_at; Type: TRIGGER; Schema: offers; Owner: postgres
--

CREATE TRIGGER update_offer_reservations_updated_at BEFORE UPDATE ON offers.offer_reservations FOR EACH ROW EXECUTE FUNCTION offers.update_updated_at_column();


--
-- Name: user_behavior_metrics update_user_behavior_metrics_updated_at; Type: TRIGGER; Schema: offers; Owner: postgres
--

CREATE TRIGGER update_user_behavior_metrics_updated_at BEFORE UPDATE ON offers.user_behavior_metrics FOR EACH ROW EXECUTE FUNCTION offers.update_updated_at_column();


--
-- Name: user_behavior_metrics update_user_segment_trigger; Type: TRIGGER; Schema: offers; Owner: postgres
--

CREATE TRIGGER update_user_segment_trigger BEFORE INSERT OR UPDATE ON offers.user_behavior_metrics FOR EACH ROW EXECUTE FUNCTION offers.update_user_segment();


--
-- Name: volume_bonus_tracking update_volume_tracking_updated_at; Type: TRIGGER; Schema: offers; Owner: postgres
--

CREATE TRIGGER update_volume_tracking_updated_at BEFORE UPDATE ON offers.volume_bonus_tracking FOR EACH ROW EXECUTE FUNCTION offers.update_updated_at_column();


--
-- Name: alembic_version alembic_version_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER alembic_version_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.alembic_version FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: consultant_payouts consultant_payouts_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER consultant_payouts_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.consultant_payouts FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: consultant_wallets consultant_wallets_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER consultant_wallets_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.consultant_wallets FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: consultants consultants_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER consultants_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.consultants FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: coupons coupons_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER coupons_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.coupons FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: invoice_line_items invoice_line_items_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER invoice_line_items_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.invoice_line_items FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: invoices invoices_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER invoices_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.invoices FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: kombu_message kombu_message_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER kombu_message_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.kombu_message FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: kombu_queue kombu_queue_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER kombu_queue_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.kombu_queue FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: payment_gateways payment_gateways_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER payment_gateways_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.payment_gateways FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: payment_orders payment_orders_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER payment_orders_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.payment_orders FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: payment_transactions payment_transactions_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER payment_transactions_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.payment_transactions FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: promotion_rules promotion_rules_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER promotion_rules_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.promotion_rules FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: quick_connect_rates quick_connect_rates_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER quick_connect_rates_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.quick_connect_rates FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: tenants tenants_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER tenants_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.tenants FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: user_wallets user_wallets_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER user_wallets_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.user_wallets FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: users users_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER users_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.users FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: wallet_orders wallet_orders_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER wallet_orders_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.wallet_orders FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: wallet_settings wallet_settings_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER wallet_settings_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.wallet_settings FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: wallet_transactions wallet_transactions_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER wallet_transactions_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.wallet_transactions FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: wallets wallets_audit; Type: TRIGGER; Schema: wallet; Owner: postgres
--

CREATE TRIGGER wallets_audit AFTER INSERT OR DELETE OR UPDATE ON wallet.wallets FOR EACH ROW EXECUTE FUNCTION audit.if_modified_func();


--
-- Name: login_activities fk_auth_users_activities; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.login_activities
    ADD CONSTRAINT fk_auth_users_activities FOREIGN KEY (auth_user_id) REFERENCES auth.auth_users(id);


--
-- Name: user_devices fk_auth_users_devices; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.user_devices
    ADD CONSTRAINT fk_auth_users_devices FOREIGN KEY (auth_user_id) REFERENCES auth.auth_users(id);


--
-- Name: otp_attempts fk_auth_users_otp_attempts; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.otp_attempts
    ADD CONSTRAINT fk_auth_users_otp_attempts FOREIGN KEY (auth_user_id) REFERENCES auth.auth_users(id);


--
-- Name: user_sessions fk_auth_users_sessions; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.user_sessions
    ADD CONSTRAINT fk_auth_users_sessions FOREIGN KEY (auth_user_id) REFERENCES auth.auth_users(id);


--
-- Name: auth_user_roles fk_auth_users_user_roles; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.auth_user_roles
    ADD CONSTRAINT fk_auth_users_user_roles FOREIGN KEY (auth_user_id) REFERENCES auth.auth_users(id);


--
-- Name: agora_consultation_session agora_consultation_session_consultation_id_fkey; Type: FK CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.agora_consultation_session
    ADD CONSTRAINT agora_consultation_session_consultation_id_fkey FOREIGN KEY (consultation_id) REFERENCES consultation.consultation(id) ON DELETE CASCADE;


--
-- Name: agora_webhook_events agora_webhook_events_consultation_session_id_fkey; Type: FK CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.agora_webhook_events
    ADD CONSTRAINT agora_webhook_events_consultation_session_id_fkey FOREIGN KEY (consultation_session_id) REFERENCES consultation.agora_consultation_session(id) ON DELETE CASCADE;


--
-- Name: feedback_comments_by_guide feedback_comments_by_guide_feedback_id_fkey; Type: FK CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.feedback_comments_by_guide
    ADD CONSTRAINT feedback_comments_by_guide_feedback_id_fkey FOREIGN KEY (feedback_id) REFERENCES consultation.feedback(id) ON DELETE CASCADE;


--
-- Name: feedback feedback_consultation_id_fkey; Type: FK CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.feedback
    ADD CONSTRAINT feedback_consultation_id_fkey FOREIGN KEY (consultation_id) REFERENCES consultation.consultation(id) ON DELETE CASCADE;


--
-- Name: consultation_quality_metrics fk_consultation; Type: FK CONSTRAINT; Schema: consultation; Owner: postgres
--

ALTER TABLE ONLY consultation.consultation_quality_metrics
    ADD CONSTRAINT fk_consultation FOREIGN KEY (consultation_id) REFERENCES consultation.consultation(id) ON DELETE CASCADE;


--
-- Name: customer_address fk_customer_address_address_id; Type: FK CONSTRAINT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.customer_address
    ADD CONSTRAINT fk_customer_address_address_id FOREIGN KEY (address_id) REFERENCES customers.address(address_id) ON DELETE CASCADE;


--
-- Name: customer_address fk_customer_address_customer_id; Type: FK CONSTRAINT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.customer_address
    ADD CONSTRAINT fk_customer_address_customer_id FOREIGN KEY (customer_id) REFERENCES customers.customer(customer_id) ON DELETE CASCADE;


--
-- Name: customer_profile fk_customer_profile_customer_id; Type: FK CONSTRAINT; Schema: customers; Owner: postgres
--

ALTER TABLE ONLY customers.customer_profile
    ADD CONSTRAINT fk_customer_profile_customer_id FOREIGN KEY (customer_id) REFERENCES customers.customer(customer_id) ON DELETE CASCADE;


--
-- Name: addresses addresses_guide_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.addresses
    ADD CONSTRAINT addresses_guide_id_fkey FOREIGN KEY (guide_id) REFERENCES guide.guide_profile(id) ON DELETE CASCADE;


--
-- Name: agreement agreement_guide_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.agreement
    ADD CONSTRAINT agreement_guide_id_fkey FOREIGN KEY (guide_id) REFERENCES guide.guide_profile(id) ON DELETE CASCADE;


--
-- Name: bank_account bank_account_guide_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.bank_account
    ADD CONSTRAINT bank_account_guide_id_fkey FOREIGN KEY (guide_id) REFERENCES guide.guide_profile(id) ON DELETE CASCADE;


--
-- Name: guide_profile fk_referrer_code; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_profile
    ADD CONSTRAINT fk_referrer_code FOREIGN KEY (referrer_code) REFERENCES guide.guide_profile(referral_code) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: guide_languages guide_languages_guide_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_languages
    ADD CONSTRAINT guide_languages_guide_id_fkey FOREIGN KEY (guide_id) REFERENCES guide.guide_profile(id) ON DELETE CASCADE;


--
-- Name: guide_languages guide_languages_language_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_languages
    ADD CONSTRAINT guide_languages_language_id_fkey FOREIGN KEY (language_id) REFERENCES guide.languages(id) ON DELETE CASCADE;


--
-- Name: guide_profile_audit guide_profile_audit_guide_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_profile_audit
    ADD CONSTRAINT guide_profile_audit_guide_id_fkey FOREIGN KEY (guide_id) REFERENCES guide.guide_profile(id) ON DELETE SET NULL;


--
-- Name: CONSTRAINT guide_profile_audit_guide_id_fkey ON guide_profile_audit; Type: COMMENT; Schema: guide; Owner: postgres
--

COMMENT ON CONSTRAINT guide_profile_audit_guide_id_fkey ON guide.guide_profile_audit IS 'Preserves audit history when guide account is soft deleted';


--
-- Name: guide_skills guide_skills_guide_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_skills
    ADD CONSTRAINT guide_skills_guide_id_fkey FOREIGN KEY (guide_id) REFERENCES guide.guide_profile(id) ON DELETE CASCADE;


--
-- Name: guide_skills guide_skills_skill_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.guide_skills
    ADD CONSTRAINT guide_skills_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES guide.skills(id) ON DELETE CASCADE;


--
-- Name: kyc_document kyc_document_guide_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.kyc_document
    ADD CONSTRAINT kyc_document_guide_id_fkey FOREIGN KEY (guide_id) REFERENCES guide.guide_profile(id) ON DELETE CASCADE;


--
-- Name: media media_guide_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.media
    ADD CONSTRAINT media_guide_id_fkey FOREIGN KEY (guide_id) REFERENCES guide.guide_profile(id) ON DELETE CASCADE;


--
-- Name: saved_messages saved_messages_guide_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.saved_messages
    ADD CONSTRAINT saved_messages_guide_id_fkey FOREIGN KEY (guide_id) REFERENCES guide.guide_profile(id) ON DELETE CASCADE;


--
-- Name: verification verification_agreement_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.verification
    ADD CONSTRAINT verification_agreement_id_fkey FOREIGN KEY (agreement_id) REFERENCES guide.agreement(id);


--
-- Name: verification verification_bank_account_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.verification
    ADD CONSTRAINT verification_bank_account_id_fkey FOREIGN KEY (bank_account_id) REFERENCES guide.bank_account(id);


--
-- Name: verification verification_guide_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.verification
    ADD CONSTRAINT verification_guide_id_fkey FOREIGN KEY (guide_id) REFERENCES guide.guide_profile(id) ON DELETE CASCADE;


--
-- Name: verification verification_kyc_document_id_fkey; Type: FK CONSTRAINT; Schema: guide; Owner: postgres
--

ALTER TABLE ONLY guide.verification
    ADD CONSTRAINT verification_kyc_document_id_fkey FOREIGN KEY (kyc_document_id) REFERENCES guide.kyc_document(id);


--
-- Name: delivery_attempts fk_delivery_attempts_notification; Type: FK CONSTRAINT; Schema: notifications; Owner: postgres
--

ALTER TABLE ONLY notifications.delivery_attempts
    ADD CONSTRAINT fk_delivery_attempts_notification FOREIGN KEY (event_id) REFERENCES notifications.notifications(event_id) ON DELETE CASCADE;


--
-- Name: offer_campaigns offer_campaigns_offer_id_fkey; Type: FK CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.offer_campaigns
    ADD CONSTRAINT offer_campaigns_offer_id_fkey FOREIGN KEY (offer_id) REFERENCES offers.offer_definitions(offer_id) ON DELETE CASCADE;


--
-- Name: offer_consumptions offer_consumptions_offer_id_fkey; Type: FK CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.offer_consumptions
    ADD CONSTRAINT offer_consumptions_offer_id_fkey FOREIGN KEY (offer_id) REFERENCES offers.offer_definitions(offer_id) ON DELETE CASCADE;


--
-- Name: offer_consumptions offer_consumptions_reservation_id_fkey; Type: FK CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.offer_consumptions
    ADD CONSTRAINT offer_consumptions_reservation_id_fkey FOREIGN KEY (reservation_id) REFERENCES offers.offer_reservations(reservation_id) ON DELETE CASCADE;


--
-- Name: offer_reservations offer_reservations_offer_id_fkey; Type: FK CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.offer_reservations
    ADD CONSTRAINT offer_reservations_offer_id_fkey FOREIGN KEY (offer_id) REFERENCES offers.offer_definitions(offer_id) ON DELETE CASCADE;


--
-- Name: user_milestone_progress user_milestone_progress_offer_id_fkey; Type: FK CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.user_milestone_progress
    ADD CONSTRAINT user_milestone_progress_offer_id_fkey FOREIGN KEY (offer_id) REFERENCES offers.offer_definitions(offer_id) ON DELETE CASCADE;


--
-- Name: volume_bonus_tracking volume_bonus_tracking_offer_id_fkey; Type: FK CONSTRAINT; Schema: offers; Owner: postgres
--

ALTER TABLE ONLY offers.volume_bonus_tracking
    ADD CONSTRAINT volume_bonus_tracking_offer_id_fkey FOREIGN KEY (offer_id) REFERENCES offers.offer_definitions(offer_id) ON DELETE CASCADE;


--
-- Name: kombu_message FK_kombu_message_queue; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.kombu_message
    ADD CONSTRAINT "FK_kombu_message_queue" FOREIGN KEY (queue_id) REFERENCES wallet.kombu_queue(id);


--
-- Name: consultant_payouts consultant_payouts_consultant_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.consultant_payouts
    ADD CONSTRAINT consultant_payouts_consultant_id_fkey FOREIGN KEY (consultant_id) REFERENCES wallet.consultant_wallets(consultant_id);


--
-- Name: consultants consultants_tenant_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.consultants
    ADD CONSTRAINT consultants_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES wallet.tenants(id);


--
-- Name: invoice_line_items invoice_line_items_invoice_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.invoice_line_items
    ADD CONSTRAINT invoice_line_items_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES wallet.invoices(invoice_id);


--
-- Name: invoices invoices_payment_order_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.invoices
    ADD CONSTRAINT invoices_payment_order_id_fkey FOREIGN KEY (payment_order_id) REFERENCES wallet.payment_orders(payment_order_id);


--
-- Name: invoices invoices_user_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.invoices
    ADD CONSTRAINT invoices_user_id_fkey FOREIGN KEY (user_id) REFERENCES wallet.user_wallets(user_id);


--
-- Name: payment_orders payment_orders_gateway_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_orders
    ADD CONSTRAINT payment_orders_gateway_id_fkey FOREIGN KEY (gateway_id) REFERENCES wallet.payment_gateways(gateway_id);


--
-- Name: payment_orders payment_orders_user_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_orders
    ADD CONSTRAINT payment_orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES wallet.user_wallets(user_id);


--
-- Name: payment_transactions payment_transactions_payment_order_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.payment_transactions
    ADD CONSTRAINT payment_transactions_payment_order_id_fkey FOREIGN KEY (payment_order_id) REFERENCES wallet.payment_orders(payment_order_id);


--
-- Name: users users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.users
    ADD CONSTRAINT users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES wallet.tenants(id);


--
-- Name: wallet_orders wallet_orders_consultant_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_orders
    ADD CONSTRAINT wallet_orders_consultant_id_fkey FOREIGN KEY (consultant_id) REFERENCES wallet.consultant_wallets(consultant_id);


--
-- Name: wallet_orders wallet_orders_payout_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_orders
    ADD CONSTRAINT wallet_orders_payout_id_fkey FOREIGN KEY (payout_id) REFERENCES wallet.consultant_payouts(payout_id);


--
-- Name: wallet_orders wallet_orders_user_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_orders
    ADD CONSTRAINT wallet_orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES wallet.user_wallets(user_id);


--
-- Name: wallet_transactions wallet_transactions_gateway_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_transactions
    ADD CONSTRAINT wallet_transactions_gateway_id_fkey FOREIGN KEY (gateway_id) REFERENCES wallet.payment_gateways(gateway_id);


--
-- Name: wallet_transactions wallet_transactions_invoice_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_transactions
    ADD CONSTRAINT wallet_transactions_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES wallet.invoices(invoice_id);


--
-- Name: wallet_transactions wallet_transactions_order_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_transactions
    ADD CONSTRAINT wallet_transactions_order_id_fkey FOREIGN KEY (order_id) REFERENCES wallet.wallet_orders(order_id);


--
-- Name: wallet_transactions wallet_transactions_user_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallet_transactions
    ADD CONSTRAINT wallet_transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES wallet.user_wallets(user_id);


--
-- Name: wallets wallets_user_id_fkey; Type: FK CONSTRAINT; Schema: wallet; Owner: postgres
--

ALTER TABLE ONLY wallet.wallets
    ADD CONSTRAINT wallets_user_id_fkey FOREIGN KEY (user_id) REFERENCES wallet.users(user_id);


--
-- Name: SCHEMA admin; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA admin TO readonly_user;


--
-- Name: SCHEMA auth; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA auth TO readonly_user;


--
-- Name: SCHEMA consultation; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA consultation TO readonly_user;


--
-- Name: SCHEMA customers; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA customers TO readonly_user;


--
-- Name: SCHEMA guide; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA guide TO readonly_user;


--
-- Name: SCHEMA notifications; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA notifications TO PUBLIC;
GRANT USAGE ON SCHEMA notifications TO readonly_user;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO readonly_user;


--
-- Name: SCHEMA wallet; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA wallet TO readonly_user;


--
-- Name: TABLE admin_users; Type: ACL; Schema: admin; Owner: postgres
--

GRANT SELECT ON TABLE admin.admin_users TO readonly_user;


--
-- Name: TABLE alembic_version; Type: ACL; Schema: admin; Owner: postgres
--

GRANT SELECT ON TABLE admin.alembic_version TO readonly_user;


--
-- Name: TABLE audit_logs; Type: ACL; Schema: admin; Owner: postgres
--

GRANT SELECT ON TABLE admin.audit_logs TO readonly_user;


--
-- Name: TABLE logged_actions; Type: ACL; Schema: audit; Owner: postgres
--

GRANT SELECT ON TABLE audit.logged_actions TO PUBLIC;


--
-- Name: TABLE auth_user_roles; Type: ACL; Schema: auth; Owner: postgres
--

GRANT SELECT ON TABLE auth.auth_user_roles TO readonly_user;


--
-- Name: TABLE auth_users; Type: ACL; Schema: auth; Owner: postgres
--

GRANT SELECT ON TABLE auth.auth_users TO readonly_user;


--
-- Name: TABLE casbin_rules; Type: ACL; Schema: auth; Owner: postgres
--

GRANT SELECT ON TABLE auth.casbin_rules TO readonly_user;


--
-- Name: TABLE login_activities; Type: ACL; Schema: auth; Owner: postgres
--

GRANT SELECT ON TABLE auth.login_activities TO readonly_user;


--
-- Name: TABLE otp_attempts; Type: ACL; Schema: auth; Owner: postgres
--

GRANT SELECT ON TABLE auth.otp_attempts TO readonly_user;


--
-- Name: TABLE user_devices; Type: ACL; Schema: auth; Owner: postgres
--

GRANT SELECT ON TABLE auth.user_devices TO readonly_user;


--
-- Name: TABLE user_sessions; Type: ACL; Schema: auth; Owner: postgres
--

GRANT SELECT ON TABLE auth.user_sessions TO readonly_user;


--
-- Name: TABLE agora_consultation_session; Type: ACL; Schema: consultation; Owner: postgres
--

GRANT SELECT ON TABLE consultation.agora_consultation_session TO readonly_user;


--
-- Name: TABLE agora_webhook_events; Type: ACL; Schema: consultation; Owner: postgres
--

GRANT SELECT ON TABLE consultation.agora_webhook_events TO readonly_user;


--
-- Name: TABLE consultation; Type: ACL; Schema: consultation; Owner: postgres
--

GRANT SELECT ON TABLE consultation.consultation TO readonly_user;


--
-- Name: TABLE consultation_analytics; Type: ACL; Schema: consultation; Owner: postgres
--

GRANT SELECT ON TABLE consultation.consultation_analytics TO readonly_user;


--
-- Name: TABLE consultation_quality_metrics; Type: ACL; Schema: consultation; Owner: postgres
--

GRANT SELECT ON TABLE consultation.consultation_quality_metrics TO readonly_user;


--
-- Name: TABLE feedback; Type: ACL; Schema: consultation; Owner: postgres
--

GRANT SELECT ON TABLE consultation.feedback TO readonly_user;


--
-- Name: TABLE feedback_comments_by_guide; Type: ACL; Schema: consultation; Owner: postgres
--

GRANT SELECT ON TABLE consultation.feedback_comments_by_guide TO readonly_user;


--
-- Name: TABLE guide_performance; Type: ACL; Schema: consultation; Owner: postgres
--

GRANT SELECT ON TABLE consultation.guide_performance TO readonly_user;


--
-- Name: TABLE address; Type: ACL; Schema: customers; Owner: postgres
--

GRANT SELECT ON TABLE customers.address TO readonly_user;


--
-- Name: TABLE customer; Type: ACL; Schema: customers; Owner: postgres
--

GRANT SELECT ON TABLE customers.customer TO readonly_user;


--
-- Name: TABLE customer_address; Type: ACL; Schema: customers; Owner: postgres
--

GRANT SELECT ON TABLE customers.customer_address TO readonly_user;


--
-- Name: TABLE customer_profile; Type: ACL; Schema: customers; Owner: postgres
--

GRANT SELECT ON TABLE customers.customer_profile TO readonly_user;


--
-- Name: TABLE addresses; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.addresses TO readonly_user;


--
-- Name: TABLE agreement; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.agreement TO readonly_user;


--
-- Name: TABLE bank_account; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.bank_account TO readonly_user;


--
-- Name: TABLE guide_languages; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.guide_languages TO readonly_user;


--
-- Name: TABLE guide_profile; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.guide_profile TO readonly_user;


--
-- Name: TABLE guide_profile_audit; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.guide_profile_audit TO readonly_user;


--
-- Name: TABLE guide_skills; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.guide_skills TO readonly_user;


--
-- Name: TABLE kyc_document; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.kyc_document TO readonly_user;


--
-- Name: TABLE languages; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.languages TO readonly_user;


--
-- Name: TABLE media; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.media TO readonly_user;


--
-- Name: TABLE saved_messages; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.saved_messages TO readonly_user;


--
-- Name: TABLE skills; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.skills TO readonly_user;


--
-- Name: TABLE verification; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.verification TO readonly_user;


--
-- Name: TABLE verification_audit_log; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.verification_audit_log TO readonly_user;


--
-- Name: TABLE vw_guide_current_verifications; Type: ACL; Schema: guide; Owner: postgres
--

GRANT SELECT ON TABLE guide.vw_guide_current_verifications TO readonly_user;


--
-- Name: TABLE client_events; Type: ACL; Schema: notifications; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE notifications.client_events TO PUBLIC;
GRANT SELECT ON TABLE notifications.client_events TO readonly_user;


--
-- Name: TABLE delivery_attempts; Type: ACL; Schema: notifications; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE notifications.delivery_attempts TO PUBLIC;
GRANT SELECT ON TABLE notifications.delivery_attempts TO readonly_user;


--
-- Name: TABLE escalation_rules; Type: ACL; Schema: notifications; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE notifications.escalation_rules TO PUBLIC;
GRANT SELECT ON TABLE notifications.escalation_rules TO readonly_user;


--
-- Name: TABLE notifications; Type: ACL; Schema: notifications; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE notifications.notifications TO PUBLIC;
GRANT SELECT ON TABLE notifications.notifications TO readonly_user;


--
-- Name: TABLE auth_schema_migrations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.auth_schema_migrations TO readonly_user;


--
-- Name: TABLE celery_taskmeta; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.celery_taskmeta TO readonly_user;


--
-- Name: TABLE celery_tasksetmeta; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.celery_tasksetmeta TO readonly_user;


--
-- Name: TABLE consultation_schema_migrations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.consultation_schema_migrations TO readonly_user;


--
-- Name: TABLE customers_schema_migrations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.customers_schema_migrations TO readonly_user;


--
-- Name: TABLE guide_schema_migrations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.guide_schema_migrations TO readonly_user;


--
-- Name: TABLE notifications_schema_migrations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.notifications_schema_migrations TO readonly_user;


--
-- Name: TABLE offers_schema_migrations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.offers_schema_migrations TO readonly_user;


--
-- Name: TABLE schema_migrations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.schema_migrations TO readonly_user;


--
-- Name: SEQUENCE task_id_sequence; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.task_id_sequence TO readonly_user;


--
-- Name: SEQUENCE taskset_id_sequence; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.taskset_id_sequence TO readonly_user;


--
-- Name: TABLE alembic_version; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.alembic_version TO readonly_user;


--
-- Name: TABLE consultant_payouts; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.consultant_payouts TO readonly_user;


--
-- Name: TABLE consultant_wallets; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.consultant_wallets TO readonly_user;


--
-- Name: TABLE consultants; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.consultants TO readonly_user;


--
-- Name: TABLE coupons; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.coupons TO readonly_user;


--
-- Name: TABLE invoice_line_items; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.invoice_line_items TO readonly_user;


--
-- Name: TABLE invoices; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.invoices TO readonly_user;


--
-- Name: TABLE kombu_message; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.kombu_message TO readonly_user;


--
-- Name: TABLE kombu_queue; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.kombu_queue TO readonly_user;


--
-- Name: TABLE payment_gateways; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.payment_gateways TO readonly_user;


--
-- Name: TABLE payment_orders; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.payment_orders TO readonly_user;


--
-- Name: TABLE payment_transactions; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.payment_transactions TO readonly_user;


--
-- Name: TABLE promotion_rules; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.promotion_rules TO readonly_user;


--
-- Name: TABLE quick_connect_rates; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.quick_connect_rates TO readonly_user;


--
-- Name: TABLE refund_audit; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.refund_audit TO readonly_user;


--
-- Name: TABLE tenants; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.tenants TO readonly_user;


--
-- Name: TABLE user_wallets; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.user_wallets TO readonly_user;


--
-- Name: TABLE users; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.users TO readonly_user;


--
-- Name: TABLE wallet_orders; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.wallet_orders TO readonly_user;


--
-- Name: TABLE wallet_settings; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.wallet_settings TO readonly_user;


--
-- Name: TABLE wallet_transactions; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.wallet_transactions TO readonly_user;


--
-- Name: TABLE wallets; Type: ACL; Schema: wallet; Owner: postgres
--

GRANT SELECT ON TABLE wallet.wallets TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: admin; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA admin GRANT ALL ON SEQUENCES TO postgres;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: admin; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA admin GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA admin GRANT SELECT ON TABLES TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: auth; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA auth GRANT SELECT ON TABLES TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: consultation; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA consultation GRANT SELECT ON TABLES TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: customers; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA customers GRANT SELECT ON TABLES TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: guide; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA guide GRANT SELECT ON TABLES TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: notifications; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA notifications GRANT SELECT ON TABLES TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT USAGE ON SEQUENCES TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: wallet; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA wallet GRANT SELECT ON TABLES TO readonly_user;


--
-- PostgreSQL database dump complete
--

\unrestrict wfHwuW3ZIxLGrE7uPMjnfe3DGZLdkvKQN9Ak5eY6oIL0WWGUHZUudL8a9tRvI2S

