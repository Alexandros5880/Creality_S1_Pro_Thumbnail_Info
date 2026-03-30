# Marketplace Checklist

This package is locally installable as a Cura plugin, but Marketplace publication still requires manual submission work.

## Included in this repo

- plugin entrypoint
- plugin metadata
- license file
- build script for zip packaging
- plugin README
- draft listing text
- screenshot checklist

## Files To Use

- package zip: `dist/CrealityS1ProAutoThumbnail-1.1.0.zip` or newer build output
- listing draft: `MARKETPLACE_LISTING.md`
- screenshot plan: `SCREENSHOT_CHECKLIST.md`
- release notes: `CHANGELOG.md`

## Still Needed Before Submission

- final publisher identity and contact details
- final screenshots for the listing
- tested compatibility statement for the exact Cura versions you want to claim
- final support URL or repository URL
- submission through the UltiMaker Marketplace flow

## Notes

- The packaged plugin metadata and zip version should always match before submission.
- Rebuild the archive after every source change so `dist` does not contain stale release files.
- The exact Marketplace submission workflow may change over time.
- This checklist is a practical release checklist, not a guarantee of every Marketplace requirement.
