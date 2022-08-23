-- Assumes the existence of a `chaotic` role. You can name it however you want.
CREATE TABLE business (
    id bigint NOT NULL,
    money integer NOT NULL,
    bank integer NOT NULL,
    bank_max integer NOT NULL,
    streak integer NOT NULL,
    last_daily integer NOT NULL,
    steal_streak integer NOT NULL
);


ALTER TABLE business ADD CONSTRAINT business_id_primary
  PRIMARY KEY (id);

ALTER TABLE business OWNER TO chaotic;
