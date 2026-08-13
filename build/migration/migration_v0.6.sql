-- Add a color column for the hikes
ALTER TABLE hikes
ADD COLUMN IF NOT EXISTS color VARCHAR(7) DEFAULT '#000000';

-- Add a color column for the hikes in the magic links
ALTER TABLE magic_links
ADD COLUMN IF NOT EXISTS color VARCHAR(7) DEFAULT '#000000';

-- Remove the primary key constraint that worked before when there was one hike per magic link
ALTER TABLE magic_links
DROP CONSTRAINT magic_links_pkey;

-- Add a new primary key that combines the magic link (id) with the hike id
ALTER TABLE magic_links 
ADD CONSTRAINT magic_links_pkey PRIMARY KEY (id, hike_id);