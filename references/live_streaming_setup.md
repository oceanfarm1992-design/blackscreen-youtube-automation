# 24/7 YouTube Live — Free Cloud Setup

Run a permanent black-screen music live stream (like "lofi radio") entirely in the
cloud, on a **free** Oracle Cloud VM. Your PC is never involved once it's running.

How it works: a tiny always-on VM runs `ffmpeg`, streaming the black `#0D0D0D`
branded frame plus audio to YouTube's RTMP ingest. You run **one dedicated 24/7
stream per music** (Rain, Waterfall, Forest, Deep Sleep, Indian, Romantic, Romantic
Night) — each its own YouTube broadcast with unique title/keywords, so they're
distinct content, not duplicates. A `systemd` template service keeps each one alive
and auto-restarts on drop. Audio is regenerated daily (fresh seeds) so no stream
loops one identical file forever. A still-image music stream uses almost no CPU or
bandwidth, so a single free VM can run all of them.

> **Scale sensibly:** one stream per *distinct* music is fine. Do NOT clone the same
> stream across many channels for volume — that reads as spam and risks suspension.

---

## Part A — Enable live on YouTube & get your stream key  🙋

1. **Enable live streaming** (one time): YouTube Studio → **Create → Go Live**.
   First activation requires a **verified phone number** and can take **up to 24h**.
   Your channel must have **no live-streaming restrictions** in the last 90 days.
2. Once enabled: **Go Live → Stream** (the "Streaming software" tab).
3. Set the stream's **title, description, category (Music), thumbnail**, and
   **visibility = Public**.
4. Under **Stream settings**, copy the **Stream key** (looks like `xxxx-xxxx-xxxx-xxxx`).
   The ingest URL is `rtmp://a.rtmp.youtube.com/live2` (already set in the script).
   - Use a **persistent/permanent** stream key so it stays valid across reconnects.

Keep the stream key secret — treat it like a password.

---

## Part B — Create the free Oracle Cloud VM  🙋

1. Sign up at **cloud.oracle.com** (a card is required for identity verification;
   **Always Free** resources are not charged).
2. **Menu → Compute → Instances → Create instance.**
   - **Image:** Canonical **Ubuntu 22.04** (or 24.04).
   - **Shape:** **VM.Standard.A1.Flex** (Ampere ARM — "Always Free eligible";
     1–2 OCPU / 6–12 GB is more than enough). If A1 capacity is unavailable in your
     region, use **VM.Standard.E2.1.Micro** (also Always Free).
   - **SSH keys:** upload your public key (or let Oracle generate one and download it).
3. **Create**, then note the instance's **public IP address**.
   - Outbound RTMP is allowed by default — no inbound firewall changes needed
     (only SSH/port 22, which is open by default).

---

## Part C — Install and start the stream  🙋 (I built the scripts)

SSH into the VM (user is `ubuntu` on Ubuntu images):

```bash
ssh ubuntu@YOUR_VM_IP
```

Then:

```bash
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/oceanfarm1992-design/blackscreen-youtube-automation.git
cd blackscreen-youtube-automation
sudo bash stream/setup.sh
```

`setup.sh` will:
- install ffmpeg + Python deps,
- generate the audio loops (all 7 musics),
- install a `youtube-live@<theme>` systemd **template** service,
- **prompt you for a stream key per music** — enter a key to run that music as its
  own 24/7 stream, or leave blank to skip it (keys stored root-only in
  `/etc/youtube-live/<theme>.env`),
- add a **daily 04:17 UTC** job that regenerates fresh audio and restarts the streams,
- start one stream per music you gave a key for.

**One stream per music.** Create a separate **live broadcast** in YouTube Studio for
each music (each with its own title/thumbnail/keys — see `live_seo.md`), and paste that
broadcast's stream key when `setup.sh` asks for that music. Start with 2–3 and scale up.

Within ~30–60s each YouTube live dashboard should show its incoming stream as
**healthy/live**.

---

## Managing it

```bash
systemctl status 'youtube-live@*'          # all streams at once
journalctl -u youtube-live@rain -f         # one stream's live logs
sudo systemctl restart youtube-live@rain   # restart one stream
sudo systemctl stop youtube-live@indian    # stop one stream
sudo systemctl start youtube-live@forest   # start one (after adding its key)
bash stream/refresh_audio.sh               # regenerate audio loops on demand
```

To add another music later: create its YouTube broadcast, then
`echo "STREAM_KEY=..." | sudo tee /etc/youtube-live/<theme>.env` and
`sudo systemctl enable --now youtube-live@<theme>`.

To change what plays, edit `THEMES` / `LOOP_SECONDS` in
[`stream/refresh_audio.sh`](../stream/refresh_audio.sh); to change bitrate/fps, edit
[`stream/stream_live.sh`](../stream/stream_live.sh).

---

## Troubleshooting

- **Dashboard says "no data":** the key is wrong or egress is blocked. Re-check the
  key in `/etc/youtube-live.env`; confirm the VM can reach the internet.
- **Stream keeps reconnecting:** the VM is undersized or bandwidth-limited — a static
  image stream shouldn't do this on A1; lower `-b:v` in `stream_live.sh` if needed.
- **"This live stream is not allowed":** live isn't enabled yet, or the channel has a
  live restriction — see Part A step 1.
- **Audio sounds repetitive:** shorten the daily refresh interval or add more musics
  to the rotation; each day's loops use a new seed so files are never identical.

## Notes

- Content is original (synthesized), so it isn't "reused" third-party content. Keep the
  daily refresh on so the stream doesn't loop one identical file indefinitely.
- This is separate from the daily VOD uploads (GitHub Actions) — you can run both.
- The VM only needs the repo + a stream key; no YouTube API/OAuth secrets are used for
  live (RTMP push uses the stream key, not the Data API), so there's **no upload-quota
  cost** for the live stream.
