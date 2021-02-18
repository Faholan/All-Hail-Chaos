CREATE TABLE stats.guilds (
    number integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL
);


ALTER TABLE stats.guilds ALTER "timestamp" SET DEFAULT now();

ALTER TABLE stats.guilds OWNER TO chaotic;

GRANT SELECT ON stats.guilds TO grafana;

CREATE TABLE stats.usage (
    command text NOT NULL,
    count integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL
);


ALTER TABLE stats.usage ALTER count SET DEFAULT 1;

ALTER TABLE stats.usage OWNER TO chaotic;

GRANT SELECT ON stats.usage TO grafana;
