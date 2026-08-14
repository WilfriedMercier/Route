-- Add a color column for the hikes
ALTER TABLE hikes
ADD COLUMN IF NOT EXISTS color VARCHAR(7) DEFAULT '#000000';

-- Rename the magic link table to a clearer name
ALTER TABLE magic_links
RENAME TO magic_links_props;

-- Create a new table containing all the magic links
DROP TABLE IF EXISTS magic_links;
CREATE TABLE magic_links (
    id TEXT PRIMARY KEY
);

-- Add a color column for the hikes in the magic links props table
ALTER TABLE magic_links_props
ADD COLUMN IF NOT EXISTS color VARCHAR(7) DEFAULT '#000000';

-- Remove the primary key constraint that worked before when there was one hike per magic link
ALTER TABLE magic_links_props
DROP CONSTRAINT magic_links_pkey;

-- Remove the old foreign key constraint on the hike id
ALTER TABLE magic_links_props
DROP CONSTRAINT fk_bridge_hike;

-- Add a new foreign key constraint on the hike id
ALTER TABLE magic_links_props
ADD CONSTRAINT fk_bridge_hike_id
FOREIGN KEY (hike_id) REFERENCES hikes(id)
ON DELETE CASCADE;

-- Add the magic links already present in the old magic_links table in the new one
INSERT INTO magic_links (id)
SELECT DISTINCT id
FROM magic_links_props;

-- Add a new foreign key constraint on the magic link
ALTER TABLE magic_links_props
ADD CONSTRAINT fk_bridge_magic_links
FOREIGN KEY (id) REFERENCES magic_links(id)
ON DELETE CASCADE;

-- Add a new primary key that combines the magic link (id) with the hike id
ALTER TABLE magic_links_props
ADD CONSTRAINT magic_links_props_pkey 
PRIMARY KEY (id, hike_id);