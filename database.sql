-- Assumes the existence of a `chaotic` role. You can name it however you want.

CREATE TABLE block (
    id bigint NOT NULL
);


ALTER TABLE block ADD CONSTRAINT block_id_primary
  PRIMARY KEY (id);

ALTER TABLE block OWNER TO chaotic;

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

CREATE TABLE custom (
    guild_id bigint NOT NULL,
    owner_id bigint NOT NULL,
    name text NOT NULL,
    description text,
    arguments text[] NOT NULL,
    effect text NOT NULL,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.custom ALTER created_at SET DEFAULT now();

ALTER TABLE custom ADD CONSTRAINT unique_custom
  UNIQUE (guild_id, name);
ALTER TABLE custom ADD CONSTRAINT custom_primary
  PRIMARY KEY (name, guild_id);

ALTER TABLE custom OWNER TO chaotic;

CREATE TABLE level_guilds (
    guild_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    message text,
    title text,
    description text,
    color integer NOT NULL
);


ALTER TABLE public.level_guilds ALTER message SET DEFAULT '\U00002705 Congratulations **{name}**! You reached **level {level}**!'::text;
ALTER TABLE public.level_guilds ALTER color SET DEFAULT 3447003;

ALTER TABLE level_guilds ADD CONSTRAINT unique_level_guilds
  UNIQUE (guild_id);
ALTER TABLE level_guilds ADD CONSTRAINT primary_level_guilds
  PRIMARY KEY (guild_id);

ALTER TABLE level_guilds OWNER TO chaotic;

CREATE TABLE level_members (
    member_id bigint NOT NULL,
    guild_id bigint NOT NULL,
    xp bigint NOT NULL,
    total_xp bigint NOT NULL,
    xp_given timestamp without time zone NOT NULL,
    level integer NOT NULL
);


ALTER TABLE public.level_members ALTER level SET DEFAULT 0;

ALTER TABLE level_members ADD CONSTRAINT unique_level_members
  UNIQUE (member_id, guild_id);
ALTER TABLE level_members ADD CONSTRAINT primary_level_members
  PRIMARY KEY (member_id, guild_id);

ALTER TABLE level_members OWNER TO chaotic;

CREATE TABLE prefixes (
    ctx_id bigint NOT NULL,
    prefix text NOT NULL
);


ALTER TABLE prefixes ADD CONSTRAINT prefix_unique
  UNIQUE (ctx_id);
ALTER TABLE prefixes ADD CONSTRAINT id_primary
  PRIMARY KEY (ctx_id);

ALTER TABLE prefixes OWNER TO chaotic;

CREATE TABLE roles (
    message_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    guild_id bigint NOT NULL,
    emoji text NOT NULL,
    roleids bigint[] NOT NULL
);


ALTER TABLE roles OWNER TO chaotic;

CREATE TABLE stats (
    command text NOT NULL,
    usage_count bigint NOT NULL
);


ALTER TABLE stats ADD CONSTRAINT unique_stats
  UNIQUE (command);
ALTER TABLE stats ADD CONSTRAINT primary_stats
  PRIMARY KEY (command);

ALTER TABLE stats OWNER TO chaotic;

CREATE TABLE successes (
    id bigint NOT NULL,
    n_use_1 integer NOT NULL,
    n_use_1_state boolean NOT NULL,
    n_use_100 integer NOT NULL,
    n_use_100_state boolean NOT NULL,
    n_use_1000 integer NOT NULL,
    n_use_1000_state boolean NOT NULL,
    hidden text[],
    hidden_state boolean NOT NULL,
    dark boolean,
    dark_state boolean NOT NULL
);


ALTER TABLE public.successes ALTER n_use_1 SET DEFAULT 1;
ALTER TABLE public.successes ALTER n_use_1_state SET DEFAULT false;
ALTER TABLE public.successes ALTER n_use_100 SET DEFAULT 1;
ALTER TABLE public.successes ALTER n_use_100_state SET DEFAULT false;
ALTER TABLE public.successes ALTER n_use_1000 SET DEFAULT 1;
ALTER TABLE public.successes ALTER n_use_1000_state SET DEFAULT false;
ALTER TABLE public.successes ALTER hidden_state SET DEFAULT false;
ALTER TABLE public.successes ALTER dark_state SET DEFAULT false;

ALTER TABLE successes ADD CONSTRAINT success_primary_key
  PRIMARY KEY (id);

ALTER TABLE successes OWNER TO chaotic;

CREATE TABLE swear (
    id bigint NOT NULL,
    manual_on boolean NOT NULL,
    autoswear boolean NOT NULL,
    notification boolean NOT NULL,
    words text[] NOT NULL
);


ALTER TABLE public.swear ALTER manual_on SET DEFAULT true;
ALTER TABLE public.swear ALTER autoswear SET DEFAULT false;
ALTER TABLE public.swear ALTER notification SET DEFAULT true;
ALTER TABLE public.swear ALTER words SET DEFAULT '{}'::text[];

ALTER TABLE swear ADD CONSTRAINT id_primary_key
  PRIMARY KEY (id);

ALTER TABLE swear OWNER TO chaotic;

CREATE TABLE tag_lookup (
    name text NOT NULL,
    location_id bigint NOT NULL,
    owner_id bigint NOT NULL,
    tag_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    use_count integer NOT NULL
);


ALTER TABLE public.tag_lookup ALTER created_at SET DEFAULT now();
ALTER TABLE public.tag_lookup ALTER use_count SET DEFAULT 0;

ALTER TABLE tag_lookup ADD CONSTRAINT unique_aliases
  UNIQUE (name, location_id);

CREATE INDEX sim_index ON public.tag_lookup USING gist (name gist_trgm_ops);

ALTER TABLE tag_lookup OWNER TO chaotic;

CREATE TABLE tags (
    location_id bigint NOT NULL,
    owner_id bigint NOT NULL,
    name text NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    id integer NOT NULL,
    use_count integer NOT NULL
);


ALTER TABLE public.tags ALTER created_at SET DEFAULT now();
ALTER TABLE public.tags ALTER id SET DEFAULT nextval('tags_id_seq'::regclass);
ALTER TABLE public.tags ALTER use_count SET DEFAULT 0;

ALTER TABLE tags ADD CONSTRAINT unique_tags
  UNIQUE (location_id, name);
ALTER TABLE tags ADD CONSTRAINT tag_id_primary
  PRIMARY KEY (id);

ALTER TABLE tags OWNER TO chaotic;

CREATE TABLE threads (
    author_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    message_id bigint,
    locked boolean,
    overwrites bigint[]
);


ALTER TABLE threads ADD CONSTRAINT unique_threads
  UNIQUE (channel_id);

ALTER TABLE threads OWNER TO chaotic;
