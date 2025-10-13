package com.example.Insurance.Service;

import com.example.Insurance.board.EventMemoryStore;
import com.example.Insurance.Entity.Event;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class EventService {

    private final EventMemoryStore store;

    public Paged<Event> list(int page, int ignoredSizeParam) {
        final int size = 6;
        final int maxPages = 3;

        List<Event> all = store.findAllDesc();
        log.info("EventService.list all.size={}", all.size());

        int cappedTotal = Math.min(all.size(), size * maxPages);
        int totalPages = Math.max(1, (int)Math.ceil(cappedTotal / (double)size));
        int current = Math.min(Math.max(page, 1), totalPages);

        int from = Math.min((current - 1) * size, cappedTotal);
        int to   = Math.min(from + size, cappedTotal);
        List<Event> slice = all.subList(0, cappedTotal).subList(from, to);

        return new Paged<>(slice, current, size, totalPages, cappedTotal);
    }

    public boolean isClosed(Event p) {
        return LocalDate.now().isAfter(p.getEndDate());
    }

    @Getter
    public static class Paged<T> {
        private final List<T> content;
        private final int page;
        private final int size;
        private final int totalPages;
        private final int totalElements;

        public Paged(List<T> content, int page, int size, int totalPages, int totalElements) {
            this.content = content;
            this.page = page;
            this.size = size;
            this.totalPages = totalPages;
            this.totalElements = totalElements;
        }
    }
}
