package org.example.agentwebhook.view

import com.vaadin.flow.component.Key
import com.vaadin.flow.component.button.Button
import com.vaadin.flow.component.button.ButtonVariant
import com.vaadin.flow.component.grid.Grid
import com.vaadin.flow.component.grid.GridVariant
import com.vaadin.flow.component.html.H1
import com.vaadin.flow.component.html.Span
import com.vaadin.flow.component.icon.VaadinIcon
import com.vaadin.flow.component.notification.Notification
import com.vaadin.flow.component.orderedlayout.FlexComponent
import com.vaadin.flow.component.orderedlayout.FlexComponent.JustifyContentMode
import com.vaadin.flow.component.orderedlayout.HorizontalLayout
import com.vaadin.flow.component.orderedlayout.VerticalLayout
import com.vaadin.flow.component.textfield.TextField
import com.vaadin.flow.data.renderer.ComponentRenderer
import com.vaadin.flow.data.renderer.LocalDateTimeRenderer
import com.vaadin.flow.router.Route
import org.example.agentwebhook.entity.AssignmentScore
import org.example.agentwebhook.repository.ScoreRepository


@Route("")
class ScoreCheckView(
    private val repository: ScoreRepository
) : VerticalLayout() {
    private val grid = Grid(AssignmentScore::class.java, false)

    init {
        // 1. 전체 레이아웃 디자인 (가운데 정렬)
        setSizeFull()
        alignItems = FlexComponent.Alignment.CENTER
        justifyContentMode = JustifyContentMode.CENTER

        // 2. 제목
        val title = H1("📊 내 과제 점수 히스토리")
        title.style.set("color", "#2c3e50") // 진한 남색 스타일

        // 3. 검색 입력창 (GitHub ID만 입력)
        val githubIdField = TextField()
        githubIdField.placeholder = "GitHub ID를 입력하세요"
        githubIdField.prefixComponent = VaadinIcon.USER.create() // 아이콘 추가
        githubIdField.isClearButtonVisible = true
        githubIdField.setWidth("300px")
        githubIdField.focus() // 페이지 열리면 바로 입력 가능하게 포커스

        // 4. 조회 버튼
        val searchBtn = Button("조회", VaadinIcon.SEARCH.create())
        searchBtn.addThemeVariants(ButtonVariant.LUMO_PRIMARY) // 파란색 버튼
        searchBtn.addClickShortcut(Key.ENTER) // 엔터키 누르면 실행

        // 조회 동작 연결
        searchBtn.addClickListener { e -> searchHistory(githubIdField.value) }

        val searchLayout = HorizontalLayout(githubIdField, searchBtn)
        searchLayout.alignItems = FlexComponent.Alignment.BASELINE

        // 5. 결과 그리드(표) 설정
        configureGrid()

        // 6. 화면 조립
        add(title, searchLayout, grid)
    }

    private fun configureGrid() {
        grid.setWidth("90%")
        grid.setHeight("600px")
        grid.isVisible = false

        // [중요] 그리드 자체에 "줄바꿈 허용" 테마 적용
        // 이 설정이 있어야 내용이 많을 때 행 높이가 자동으로 늘어납니다.
        grid.addThemeVariants(GridVariant.LUMO_WRAP_CELL_CONTENT)

        // [컬럼 1] 과제명
        grid.addColumn(AssignmentScore::repoName)
            .setHeader("과제명")
            .setWidth("150px")
            .flexGrow = 0

        // [컬럼 2] PR 번호
        grid.addColumn(AssignmentScore::prNumber)
            .setHeader("PR #")
            .setWidth("80px")
            .flexGrow = 0

        // [컬럼 3] 점수
        grid.addColumn(ComponentRenderer { score: AssignmentScore? ->
            val badge = Span(score!!.score.toString() + "점")
            var theme = "badge pill"
            theme += if (score.score >= 90) " success"
            else if (score.score >= 70) " contrast"
            else " error"
            badge.getElement().themeList.add(theme)
            badge
        }).setHeader("점수").setWidth("100px").setSortable(true).flexGrow = 0

        // [컬럼 4] AI 피드백 (수정됨)
        grid.addColumn(ComponentRenderer { score: AssignmentScore? ->
            val span = Span(score!!.feedback)
            // [스타일 설정]
            // pre-wrap: 줄바꿈(\n) 인식 + 자동 줄바꿈
            span.style.set("white-space", "pre-wrap")
            span.style.set("word-break", "break-word") // 긴 단어 강제 줄바꿈
            span.style.set("line-height", "1.5") // 줄 간격
            span.setWidthFull()
            span
        })
            .setHeader("AI 피드백") // [수정] setMinWidth는 없으므로 setWidth를 사용합니다.
            // setFlexGrow(1)과 함께 쓰면 "기본 350px로 시작해서 남는 공간을 다 차지해라"가 됩니다.
            .setWidth("350px")
            .flexGrow = 1

        // [컬럼 5] 날짜
        grid.addColumn(
            LocalDateTimeRenderer(
                AssignmentScore::gradedAt,
                "yyyy-MM-dd HH:mm"
            )
        ).setHeader("채점 일시").setWidth("160px").flexGrow = 0
    }

    private fun searchHistory(studentName: String?) {
        if (studentName == null || studentName.isBlank()) {
            Notification.show("GitHub ID를 입력해주세요.", 2000, Notification.Position.MIDDLE)
            return
        }

        // 리스트 조회 호출 (최신순)
        val history = repository.findByStudentNameOrderByGradedAtDesc(studentName)

        if (history.isEmpty()) {
            grid.isVisible = false
            Notification.show("'$studentName' 님의 채점 기록이 없습니다.", 3000, Notification.Position.MIDDLE)
        } else {
            grid.isVisible = true
            grid.setItems(history)
            Notification.show(history.size.toString() + "건의 과제 내역을 불러왔습니다.", 2000, Notification.Position.BOTTOM_END)
        }
    }
}