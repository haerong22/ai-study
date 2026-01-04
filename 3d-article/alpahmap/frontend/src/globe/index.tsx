import Globe from "react-globe.gl";
import "./style.css";
import { useEffect, useState } from "react";
import Api from "../Api";
import { type Article } from "../Models";
import { GLTFLoader } from "three/examples/jsm/Addons.js";
import { Object3D } from "three";

function GlobePage() {
  const [articles, setArticles] = useState<Article[]>();
  const [selectedArticle, setSelectedArticle] = useState<Article>();
  const [isOpened, setIsOpened] = useState(false);

  useEffect(() => {
    (async () => {
      const articles = await Api.fetchArticles();

      await Promise.allSettled(
        articles.map(async (article) => {
          const arraybuffer = await Api.fetchArticleModel(article.model.id);
          const loader = new GLTFLoader();
          const model = await loader.parseAsync(arraybuffer, "");
          const object = model.scene;

          object.scale.setScalar(article.model.scale);

          article.model.object3D = object;
        })
      );

      setArticles(articles);
    })();
  }, []);

  return (
    <Globe
      backgroundImageUrl={"//unpkg.com/three-globe/example/img/night-sky.png"}
      globeImageUrl={"./earthhd.jpg"}
      bumpImageUrl={"//unpkg.com/three-globe/example/img/earth-topology.png"}
      objectsData={articles}
      objectLat={(article) => (article as Article).model.latitude}
      objectLng={(article) => (article as Article).model.longitude}
      objectAltitude={(article) => (article as Article).model.height}
      objectLabel={(article) => (article as Article).title}
      objectThreeObject={(article) =>
        (article as Article).model.object3D ?? new Object3D()
      }
      onObjectClick={(article) => {
        setSelectedArticle(article as Article);
        setIsOpened(true);
      }}
      onGlobeClick={() => setIsOpened(false)}
    />
  );
}

export default GlobePage;
