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
	"crawl_id"	INTEGER,
	FOREIGN KEY("crawl_id") REFERENCES "crawls"("id") ON DELETE CASCADE,
	FOREIGN KEY("destination_page_id") REFERENCES "pages"("id"),
	FOREIGN KEY("parent_page_id") REFERENCES "pages"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "pages" (
	"id"	INTEGER NOT NULL,
	"absolute_url"	VARCHAR NOT NULL,
	"created_on"	DATETIME,
	"content"	VARCHAR,
	"mime_id"	INTEGER,
	"crawl_id"	INTEGER,
	FOREIGN KEY("crawl_id") REFERENCES "crawls"("id") ON DELETE CASCADE,
	FOREIGN KEY("mime_id") REFERENCES "mimes"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "crawls" (
	"id"	INTEGER NOT NULL,
	"date"	DATETIME,
	"note"	VARCHAR,
	"site_id"	INTEGER,
	FOREIGN KEY("site_id") REFERENCES "sites"("id") ON DELETE CASCADE,
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
