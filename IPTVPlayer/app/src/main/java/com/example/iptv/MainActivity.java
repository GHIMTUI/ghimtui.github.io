package com.example.iptv;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;

import androidx.media3.common.MediaItem;
import androidx.media3.exoplayer.ExoPlayer;
import androidx.media3.ui.PlayerView;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends Activity {

    private static final int REQ_PICK = 1;

    private final List<Channel> channels = new ArrayList<>();
    private ExoPlayer player;
    private PlayerView playerView;
    private View listPanel;
    private ArrayAdapter<String> adapter;
    private GestureDetector gestureDetector;
    private int current = -1;

    static class Channel {
        final String name;
        final String url;
        Channel(String name, String url) { this.name = name; this.url = url; }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        listPanel = findViewById(R.id.listPanel);
        playerView = findViewById(R.id.playerView);
        playerView.setUseController(false);

        player = new ExoPlayer.Builder(this).build();
        playerView.setPlayer(player);

        ListView lv = findViewById(R.id.listChannels);
        adapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, new ArrayList<String>());
        lv.setAdapter(adapter);
        lv.setOnItemClickListener((parent, view, pos, id) -> showPlayer(pos));

        findViewById(R.id.btnOpen).setOnClickListener(v -> {
            Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("*/*");
            startActivityForResult(i, REQ_PICK);
        });

        gestureDetector = new GestureDetector(this, new GestureDetector.SimpleOnGestureListener() {
            @Override
            public boolean onDown(MotionEvent e) {
                return true;
            }

            @Override
            public boolean onFling(MotionEvent e1, MotionEvent e2, float vx, float vy) {
                if (e1 == null || e2 == null) return false;
                float dy = e2.getY() - e1.getY();
                float dx = e2.getX() - e1.getX();
                if (Math.abs(dy) > 120 && Math.abs(dy) > Math.abs(dx)) {
                    changeChannel(dy < 0 ? +1 : -1); // vuốt lên = kênh sau, xuống = kênh trước
                    return true;
                }
                return false;
            }
        });
        playerView.setOnTouchListener((v, e) -> gestureDetector.onTouchEvent(e));
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQ_PICK && resultCode == RESULT_OK && data != null && data.getData() != null) {
            loadPlaylist(data.getData());
        }
    }

    private void loadPlaylist(Uri uri) {
        try (InputStream in = getContentResolver().openInputStream(uri)) {
            List<Channel> parsed = parseM3U(in);
            channels.clear();
            channels.addAll(parsed);

            List<String> names = new ArrayList<>();
            for (Channel c : channels) names.add(c.name);
            adapter.clear();
            adapter.addAll(names);
            adapter.notifyDataSetChanged();

            Toast.makeText(this, "Đã tải " + channels.size() + " kênh", Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            Toast.makeText(this, "Lỗi đọc file: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    static List<Channel> parseM3U(InputStream in) throws IOException {
        List<Channel> list = new ArrayList<>();
        BufferedReader reader = new BufferedReader(new InputStreamReader(in, "UTF-8"));
        String line;
        String pendingName = null;
        while ((line = reader.readLine()) != null) {
            line = line.trim();
            if (line.startsWith("#EXTINF")) {
                int comma = line.lastIndexOf(',');
                pendingName = comma >= 0 ? line.substring(comma + 1).trim() : null;
            } else if (!line.isEmpty() && !line.startsWith("#")) {
                String name = (pendingName != null && !pendingName.isEmpty())
                        ? pendingName
                        : "Kênh " + (list.size() + 1);
                list.add(new Channel(name, line));
                pendingName = null;
            }
        }
        return list;
    }

    private void showPlayer(int pos) {
        listPanel.setVisibility(View.GONE);
        playerView.setVisibility(View.VISIBLE);
        playChannel(pos);
    }

    private void playChannel(int pos) {
        current = pos;
        player.setMediaItem(MediaItem.fromUri(channels.get(pos).url));
        player.prepare();
        player.play();
        Toast.makeText(this, (pos + 1) + ". " + channels.get(pos).name, Toast.LENGTH_SHORT).show();
    }

    private void changeChannel(int delta) {
        if (channels.isEmpty() || playerView.getVisibility() != View.VISIBLE) return;
        int n = channels.size();
        playChannel(((current + delta) % n + n) % n);
    }

    @Override
    public void onBackPressed() {
        if (playerView.getVisibility() == View.VISIBLE) {
            player.stop();
            playerView.setVisibility(View.GONE);
            listPanel.setVisibility(View.VISIBLE);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        player.release();
        super.onDestroy();
    }
}
