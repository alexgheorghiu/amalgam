BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "links" (
	"id"	INTEGER NOT NULL,
	"url"	VARCHAR,
	"absolute_url"	VARCHAR NOT NULL,
	"created_on"	DATETIME,
	"redirects"	VARCHAR,
	"type"	VARCHAR,
	"parent_page_id"	INTEGER,
	"destination_page_id"	INTEGER,
	FOREIGN KEY("destination_page_id") REFERENCES "pages"("id"),
	FOREIGN KEY("parent_page_id") REFERENCES "pages"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "pages" (
	"id"	INTEGER NOT NULL,
	"absolute_url"	VARCHAR NOT NULL,
	"created_on"	DATETIME,
	"content"	VARCHAR,
	"crawl_id"	INTEGER,
	"mime_id"	INTEGER,
	FOREIGN KEY("mime_id") REFERENCES "mimes"("id"),
	FOREIGN KEY("crawl_id") REFERENCES "crawls"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "crawls" (
	"id"	INTEGER NOT NULL,
	"date"	DATETIME,
	"note"	VARCHAR,
	"site_id"	INTEGER,
	FOREIGN KEY("site_id") REFERENCES "sites"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "sites" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR,
	"email"	VARCHAR,
	"password"	VARCHAR,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "settings" (
	"key"	VARCHAR NOT NULL,
	"value"	VARCHAR,
	PRIMARY KEY("key")
);
CREATE TABLE IF NOT EXISTS "mimes" (
	"id"	INTEGER NOT NULL,
	"mime"	VARCHAR,
	PRIMARY KEY("id")
);
COMMIT;
