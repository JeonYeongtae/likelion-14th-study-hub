-- ==========================================================
-- Phase 2: users 테이블에 role 컬럼 추가
-- ==========================================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user';

-- ==========================================================
-- 명세서: users 테이블에 deleted_at 추가 (소프트 딜리트)
-- ==========================================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- ==========================================================
-- Phase 2: study_rooms 테이블에 description 추가
-- ==========================================================
ALTER TABLE study_rooms ADD COLUMN IF NOT EXISTS description TEXT;

-- ==========================================================
-- Phase 3: post_images 테이블 생성
-- ==========================================================
CREATE TABLE IF NOT EXISTS post_images (
    id         SERIAL PRIMARY KEY,
    post_id    INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    image_url  TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ==========================================================
-- Phase 4: room_settings 테이블 생성
-- ==========================================================
CREATE TABLE IF NOT EXISTS room_settings (
    id            SERIAL PRIMARY KEY,
    room_id       INTEGER NOT NULL UNIQUE REFERENCES study_rooms(id) ON DELETE CASCADE,
    open_time     TIME NOT NULL DEFAULT '09:00',
    close_time    TIME NOT NULL DEFAULT '22:00',
    slot_duration INTEGER NOT NULL DEFAULT 60,
    created_at    TIMESTAMPTZ DEFAULT now(),
    updated_at    TIMESTAMPTZ
);

-- ==========================================================
-- Phase 5: study_groups 테이블 생성
-- (reservations.group_id가 이 테이블을 참조하므로 먼저 생성)
-- ==========================================================
CREATE TABLE IF NOT EXISTS study_groups (
    id              SERIAL PRIMARY KEY,
    leader_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    max_members     INTEGER NOT NULL,
    current_members INTEGER NOT NULL DEFAULT 1,
    status          VARCHAR(20) NOT NULL DEFAULT '모집중',
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ==========================================================
-- Phase 5: applications 테이블 생성
-- ==========================================================
CREATE TABLE IF NOT EXISTS applications (
    id           SERIAL PRIMARY KEY,
    group_id     INTEGER NOT NULL REFERENCES study_groups(id) ON DELETE CASCADE,
    applicant_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status       VARCHAR(20) NOT NULL DEFAULT 'pending',
    message      TEXT,
    created_at   TIMESTAMPTZ DEFAULT now(),
    UNIQUE(group_id, applicant_id)
);

-- ==========================================================
-- Phase 1 수정: reservations 테이블 구조 변경
-- reservation_time → start_time + end_time
-- Phase 6: group_id 컬럼 추가 (study_groups 생성 후 실행)
-- ==========================================================
ALTER TABLE reservations ADD COLUMN IF NOT EXISTS start_time TIMESTAMPTZ;
ALTER TABLE reservations ADD COLUMN IF NOT EXISTS end_time TIMESTAMPTZ;
ALTER TABLE reservations ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES study_groups(id) ON DELETE SET NULL;

-- 기존 reservation_time 데이터 마이그레이션
UPDATE reservations
SET start_time = reservation_time,
    end_time   = reservation_time + INTERVAL '1 hour'
WHERE start_time IS NULL AND reservation_time IS NOT NULL;

ALTER TABLE reservations ALTER COLUMN start_time SET NOT NULL;
ALTER TABLE reservations ALTER COLUMN end_time SET NOT NULL;

-- 기존 컬럼 제거 (확인 후 실행)
-- ALTER TABLE reservations DROP COLUMN IF EXISTS reservation_time;

-- ==========================================================
-- 명세서: notifications 테이블 생성
-- ==========================================================
CREATE TABLE IF NOT EXISTS notifications (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type       TEXT NOT NULL,          -- comment / reservation
    message    TEXT NOT NULL,
    related_id BIGINT,                 -- post_id 또는 reservation_id
    is_read    BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ==========================================================
-- 명세서: 탈퇴 30일 후 하드딜리트 — pg_cron 설정
-- Supabase 대시보드 > Database > Extensions 에서 pg_cron 활성화 후 실행
-- ==========================================================
-- SELECT cron.schedule(
--     'hard-delete-withdrawn-users',   -- 잡 이름
--     '0 3 * * *',                      -- 매일 새벽 3시
--     $$
--     DELETE FROM users
--     WHERE is_active = false
--       AND deleted_at IS NOT NULL
--       AND deleted_at < now() - INTERVAL '30 days';
--     $$
-- );
