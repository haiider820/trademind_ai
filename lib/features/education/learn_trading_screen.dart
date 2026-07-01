import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class LearnTradingScreen extends StatelessWidget {
  const LearnTradingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Learn Trading'),
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _loadLessons(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Failed to load lessons: ${snapshot.error}'));
          }

          final lessons = snapshot.data ?? const [];
          if (lessons.isEmpty) {
            return const Center(
              child: Text('No lessons published yet. Admin can add them from Supabase.'),
            );
          }

          final grouped = <String, List<Map<String, dynamic>>>{};
          for (final lesson in lessons) {
            final category = (lesson['category'] as String? ?? 'General').trim();
            grouped.putIfAbsent(category, () => []).add(lesson);
          }

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const Text(
                'Lessons added by admin will appear here automatically.',
                style: TextStyle(color: Colors.white70),
              ),
              const SizedBox(height: 16),
              ...grouped.entries.expand(
                (entry) => [
                  Text(
                    entry.key,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 10),
                  ...entry.value.map((lesson) => Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: _LessonCard(lesson: lesson),
                      )),
                  const SizedBox(height: 8),
                ],
              ),
            ],
          );
        },
      ),
    );
  }

  Future<List<Map<String, dynamic>>> _loadLessons() async {
    final response = await Supabase.instance.client
        .from('lessons')
        .select('id,title,category,video_url,description,thumbnail,created_at')
        .order('created_at', ascending: false);
    return List<Map<String, dynamic>>.from(response as List);
  }
}

class _LessonCard extends StatelessWidget {
  const _LessonCard({required this.lesson});

  final Map<String, dynamic> lesson;

  @override
  Widget build(BuildContext context) {
    final title = lesson['title'] as String? ?? 'Untitled lesson';
    final description = lesson['description'] as String? ?? '';
    final thumbnail = lesson['thumbnail'] as String?;
    final videoUrl = lesson['video_url'] as String?;
    final createdAt = DateTime.tryParse(lesson['created_at'] as String? ?? '');

    return Material(
      color: Theme.of(context).colorScheme.surface,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: () {},
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: thumbnail == null || thumbnail.isEmpty
                    ? Icon(Icons.play_circle_outline, color: Theme.of(context).colorScheme.primary)
                    : ClipRRect(
                        borderRadius: BorderRadius.circular(14),
                        child: Image.network(thumbnail, fit: BoxFit.cover),
                      ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                    const SizedBox(height: 4),
                    Text(
                      description,
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: Colors.white70),
                    ),
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 10,
                      runSpacing: 8,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        if (createdAt != null)
                          Text(
                            DateFormat('yMMMd').format(createdAt),
                            style: const TextStyle(color: Colors.white54, fontSize: 12),
                          ),
                        if (videoUrl != null && videoUrl.isNotEmpty)
                          const Text('Video attached', style: TextStyle(color: Colors.white54, fontSize: 12)),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
