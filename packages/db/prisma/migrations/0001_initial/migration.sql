-- CreateTable
CREATE TABLE "leagues" (
    "ligaId" TEXT NOT NULL,
    "seasonId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "level" TEXT,
    "region" TEXT,
    "source" TEXT NOT NULL,
    "scraped_at" DATETIME NOT NULL,

    PRIMARY KEY ("ligaId", "seasonId")
);

-- CreateTable
CREATE TABLE "seasons" (
    "seasonId" TEXT NOT NULL PRIMARY KEY,
    "year" INTEGER NOT NULL,
    "ligaId" TEXT NOT NULL,
    FOREIGN KEY ("ligaId") REFERENCES "leagues" ("ligaId") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "teams" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "aliases" TEXT NOT NULL DEFAULT '[]'
);

-- CreateTable
CREATE TABLE "matches" (
    "matchId" TEXT PRIMARY KEY,
    "matchNo" INTEGER,
    "spielplan_id" TEXT UNIQUE,
    "seasonId" TEXT NOT NULL,
    "ligaId" TEXT NOT NULL,
    "date" DATETIME NOT NULL,
    "homeTeamId" TEXT NOT NULL,
    "guestTeamId" TEXT NOT NULL,
    "result" TEXT,
    "status" TEXT NOT NULL,
    FOREIGN KEY ("seasonId") REFERENCES "seasons" ("seasonId") ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("ligaId") REFERENCES "leagues" ("ligaId") ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("homeTeamId") REFERENCES "teams" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("guestTeamId") REFERENCES "teams" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "players" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "aliases" TEXT NOT NULL DEFAULT '[]'
);

-- CreateTable
CREATE TABLE "boxscore_rows" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "matchId" TEXT,
    "teamId" TEXT NOT NULL,
    "playerId" TEXT,
    "playerName" TEXT NOT NULL,
    "pts" INTEGER NOT NULL DEFAULT 0,
    "3pm" INTEGER NOT NULL DEFAULT 0,
    "3pa" INTEGER NOT NULL DEFAULT 0,
    "ftm" INTEGER NOT NULL DEFAULT 0,
    "fta" INTEGER NOT NULL DEFAULT 0,
    "source" TEXT NOT NULL,
    "scraped_at" DATETIME NOT NULL,
    FOREIGN KEY ("matchId") REFERENCES "matches" ("matchId") ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY ("teamId") REFERENCES "teams" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("playerId") REFERENCES "players" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "season_stats" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "playerId" TEXT NOT NULL,
    "seasonId" TEXT NOT NULL,
    "pts" INTEGER NOT NULL DEFAULT 0,
    "g" INTEGER NOT NULL DEFAULT 0,
    "pts_g" REAL NOT NULL DEFAULT 0,
    "3pm" INTEGER NOT NULL DEFAULT 0,
    "3pa" INTEGER NOT NULL DEFAULT 0,
    "3p_pct" REAL NOT NULL DEFAULT 0,
    "ftm" INTEGER NOT NULL DEFAULT 0,
    "fta" INTEGER NOT NULL DEFAULT 0,
    "ft_pct" REAL NOT NULL DEFAULT 0,
    FOREIGN KEY ("playerId") REFERENCES "players" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("seasonId") REFERENCES "seasons" ("seasonId") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "aliases" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "entityType" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "targetId" TEXT NOT NULL,
    FOREIGN KEY ("targetId") REFERENCES "players" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("targetId") REFERENCES "teams" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "qa_issues" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "type" TEXT NOT NULL,
    "matchId" TEXT,
    "seasonId" TEXT,
    "description" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'open',
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("matchId") REFERENCES "matches" ("matchId") ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY ("seasonId") REFERENCES "seasons" ("seasonId") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "matches_matchNo_seasonId_key" ON "matches"("matchNo", "seasonId");

-- CreateIndex
CREATE UNIQUE INDEX "season_stats_playerId_seasonId_key" ON "season_stats"("playerId", "seasonId");

-- CreateIndex
CREATE UNIQUE INDEX "aliases_entityType_value_key" ON "aliases"("entityType", "value");