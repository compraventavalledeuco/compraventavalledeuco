#!/usr/bin/env python3
"""
Migrate local vehicle images to Cloudinary and update DB records.

Features:
- Detects Vehicle.images entries that are local (not starting with http)
- Attempts to find files under static/ and upload to Cloudinary
- Replaces each local path with the resulting Cloudinary secure_url
- If a file is missing, can either keep it as-is or replace with placeholder
- Dry run support to preview changes

Usage examples:
  SKIP_ROUTES=1 python migrate_local_images_to_cloudinary.py --dry-run
  SKIP_ROUTES=1 python migrate_local_images_to_cloudinary.py --batch-size 50
  # Heroku
  # heroku run bash -a <APP>
  #   export SKIP_ROUTES=1
  #   python migrate_local_images_to_cloudinary.py --batch-size 50
"""
import os
import json
import argparse
from datetime import datetime

# Lightweight app context (avoids importing routes)
os.environ.setdefault("SKIP_ROUTES", "1")

from app import app, db
from models import Vehicle

PLACEHOLDER_STATIC = 'placeholder-car.png'  # under static/


def is_http_url(url: str) -> bool:
    return url.startswith('http://') or url.startswith('https://')


def to_static_full_path(image_entry: str) -> str:
    """Resolve a local image entry to an absolute path under static/.
    Handles values like 'uploads/foo.jpg' or 'static/uploads/foo.jpg'.
    """
    # Normalize
    normalized = image_entry.lstrip('/')
    # Strip leading 'static/' if present
    if normalized.startswith('static/'):
        normalized = normalized[len('static/'):]
    # Build full path under project static dir
    project_root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(project_root, 'static', normalized)


def upload_local_file_to_cloudinary(full_path: str):
    """Upload a local file to Cloudinary using existing helper.
    Returns dict {success, url, error}.
    """
    try:
        # Import lazily to avoid overhead if not needed
        from cloudinary_storage import upload_to_cloudinary
    except Exception as e:
        return { 'success': False, 'error': f'Cloudinary import failed: {e}' }

    try:
        # Open file in binary mode
        with open(full_path, 'rb') as f:
            result = upload_to_cloudinary(f, folder='vehicle_images_migrated')
            if result and result.get('success'):
                return { 'success': True, 'url': result.get('url') }
            else:
                return { 'success': False, 'error': result.get('error', 'Unknown upload error') }
    except FileNotFoundError:
        return { 'success': False, 'error': 'File not found' }
    except Exception as e:
        return { 'success': False, 'error': str(e) }


def migrate_images(dry_run: bool, batch_size: int, replace_missing_with_placeholder: bool):
    updated = 0
    examined = 0
    missing_files = 0
    skipped_http = 0
    failed_uploads = 0
    vehicles_changed = 0

    with app.app_context():
        q = Vehicle.query.order_by(Vehicle.id.asc())
        total = q.count()
        print(f"Found {total} vehicles to examine")

        for vehicle in q.yield_per(batch_size):
            examined += 1
            changed = False
            images_list = []
            try:
                images_list = json.loads(vehicle.images) if vehicle.images else []
                if not isinstance(images_list, list):
                    images_list = []
            except Exception:
                images_list = []

            if not images_list:
                continue

            new_images = []
            for img in images_list:
                # Pass through HTTP(S) URLs unchanged
                if isinstance(img, str) and is_http_url(img):
                    skipped_http += 1
                    new_images.append(img)
                    continue

                # Resolve local file path
                full_path = to_static_full_path(str(img))
                if os.path.exists(full_path):
                    if dry_run:
                        # Simulate replacement with a Cloudinary URL placeholder
                        new_images.append(f"CLOUDINARY_URL_WOULD_BE_SET_FOR::{img}")
                        changed = True
                        updated += 1
                    else:
                        # Upload
                        res = upload_local_file_to_cloudinary(full_path)
                        if res.get('success'):
                            new_images.append(res['url'])
                            changed = True
                            updated += 1
                        else:
                            failed_uploads += 1
                            print(f"Upload failed for vehicle {vehicle.id} file {img}: {res.get('error')}")
                            # keep original entry as fallback
                            new_images.append(img)
                else:
                    missing_files += 1
                    if replace_missing_with_placeholder:
                        # Store placeholder as full static path relative
                        from flask import url_for
                        # We cannot call url_for outside request; store relative static path
                        placeholder_entry = PLACEHOLDER_STATIC
                        # Keep consistent with templates: they call url_for('static', filename=image)
                        # so we should save without 'static/' prefix
                        new_images.append(placeholder_entry)
                        changed = True
                    else:
                        new_images.append(img)

            if changed:
                vehicles_changed += 1
                if dry_run:
                    print(f"[DRY RUN] Would update Vehicle {vehicle.id}: {len(images_list)} -> {len(new_images)} images")
                else:
                    vehicle.images = json.dumps(new_images)
        
        if not dry_run:
            db.session.commit()

    print("=== Migration Summary ===")
    print(f"Examined vehicles: {examined}")
    print(f"Vehicles changed: {vehicles_changed}")
    print(f"Images uploaded: {updated}")
    print(f"HTTP images skipped: {skipped_http}")
    print(f"Missing files: {missing_files}")
    print(f"Failed uploads: {failed_uploads}")


def main():
    parser = argparse.ArgumentParser(description='Migrate local vehicle images to Cloudinary')
    parser.add_argument('--dry-run', action='store_true', help='Do not write changes to DB')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for DB iteration')
    parser.add_argument('--replace-missing-with-placeholder', action='store_true',
                        help='Replace missing local images with static placeholder-car.png')

    args = parser.parse_args()

    # Sanity: warn if Cloudinary is not configured
    cloudinary_url = os.environ.get('CLOUDINARY_URL') or os.environ.get('CLOUDINARY_CLOUD_NAME')
    if not cloudinary_url:
        print('WARNING: Cloudinary credentials not found in environment. Uploads will fail.')

    migrate_images(
        dry_run=args.dry_run,
        batch_size=args.batch_size,
        replace_missing_with_placeholder=args.replace_missing_with_placeholder
    )


if __name__ == '__main__':
    main()
