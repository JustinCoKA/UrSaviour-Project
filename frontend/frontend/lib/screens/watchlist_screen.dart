import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class WatchlistScreen extends StatefulWidget {
  final int userId;
  const WatchlistScreen({super.key, required this.userId});

  @override
  State<WatchlistScreen> createState() => _WatchlistScreenState();
}

class _WatchlistScreenState extends State<WatchlistScreen> {
  List<dynamic> watchlist = [];

  Future<void> fetchWatchlist() async {
    final url = Uri.parse('http://127.0.0.1:8000/watchlist/${widget.userId}');
    final res = await http.get(url);
    if (res.statusCode == 200) {
      setState(() {
        watchlist = jsonDecode(res.body);
      });
    }
  }

  Future<void> removeFromWatchlist(int productId) async {
    final url = Uri.parse('http://127.0.0.1:8000/watchlist/${widget.userId}/$productId');
    final res = await http.delete(url);
    if (res.statusCode == 200) {
      fetchWatchlist();
    }
  }

  @override
  void initState() {
    super.initState();
    fetchWatchlist();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("My Watchlist")),
      body: watchlist.isEmpty
          ? const Center(child: Text("No items in your watchlist"))
          : ListView.builder(
              itemCount: watchlist.length,
              itemBuilder: (context, index) {
                final item = watchlist[index];
                return Card(
                  margin: const EdgeInsets.all(8),
                  child: ListTile(
                    title: Text('Product ID: ${item["product_id"]}'),
                    subtitle: Text('Added: ${item["added_at"]}'),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete),
                      onPressed: () => removeFromWatchlist(item["product_id"]),
                    ),
                  ),
                );
              },
            ),
    );
  }
}

Add WatchlistScreen for Flutter frontend
