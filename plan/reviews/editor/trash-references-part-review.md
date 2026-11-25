# Part review: editor/trash-references (group 2 of 3)

- wrong: "`FindInScene` walks every registered component and every script field that holds an asset, at most 1,000 entities"; the limit counts the uses found (`found.size() >= limit`, `AssetReferences.h:65-67`: "at most `limit` of them"), not the entities walked; now "and lists at most 1,000 uses".
