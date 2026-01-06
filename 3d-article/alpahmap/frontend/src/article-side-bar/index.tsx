import type { Article } from "../Models";
import Markdown from "react-markdown";
import "./style.css";
import { sideBarWidth } from "../Constants";
import { useEffect, useRef } from "react";

interface ArticleSideBarProps {
  selectedArticle?: Article;
  isOpened: boolean;
}

function ArticleSideBar({ selectedArticle, isOpened }: ArticleSideBarProps) {
  const rootContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const rootContainer = rootContainerRef.current;
    if (!rootContainer) return;

    rootContainer.scrollTop = 0;
  }, [selectedArticle]);

  return (
    <div
      style={{
        left: isOpened ? 0 : -sideBarWidth,
        width: sideBarWidth,
      }}
      className="article-side-bar bg-blur-24"
    >
      <div className="title">Article</div>
      <div className="content" ref={rootContainerRef}>
        {selectedArticle ? (
          <>
            <div className="title">{selectedArticle.title}</div>
            <img
              style={{
                marginTop: 8,
                borderRadius: 8,
              }}
              src={selectedArticle.imageUrl}
            />
            <Markdown>{selectedArticle.content}</Markdown>
          </>
        ) : (
          <div className="empty-message">
            지구본에서 사회문제를 클릭해보세요
          </div>
        )}
      </div>
    </div>
  );
}

export default ArticleSideBar;
