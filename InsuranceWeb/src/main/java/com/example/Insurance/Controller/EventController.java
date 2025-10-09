package com.example.Insurance.Controller;

import com.example.Insurance.Service.EventService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.IntStream;

@Controller
@RequiredArgsConstructor
@RequestMapping("/events")
public class EventController {

    private final EventService service;

    @GetMapping("/event")
    public String list(@RequestParam(name = "page", defaultValue = "1") int page,
                       Model model) {
        var paged = service.list(page, 6);

        List<Row> rows = paged.getContent().stream().map(p -> {
            boolean closed = service.isClosed(p);
            return new Row(
                    p.getTitle(),
                    p.getSummary(),
                    p.getImageUrl(),
                    p.getStartDate().toString(),
                    p.getEndDate().toString(),
                    closed ? "종료" : "진행중",
                    closed ? "text-bg-secondary" : "text-bg-success"
            );
        }).toList();

        List<PageItem> pages = IntStream.rangeClosed(1, paged.getTotalPages())
                .mapToObj(i -> new PageItem(i, i == paged.getPage()))
                .toList();

        model.addAttribute("rows", rows);
        model.addAttribute("pages", pages);
        model.addAttribute("prevDisabled", paged.getPage() <= 1);
        model.addAttribute("nextDisabled", paged.getPage() >= paged.getTotalPages());
        model.addAttribute("prevPage", Math.max(1, paged.getPage() - 1));
        model.addAttribute("nextPage", Math.min(paged.getTotalPages(), paged.getPage() + 1));
        model.addAttribute("totalElements", paged.getTotalElements());

        return "board/event_list";
    }

    static record Row(
            String title, String summary, String imageUrl,
            String startDate, String endDate,
            String status, String statusClass) {}

    static record PageItem(int num, boolean active) {}
}
