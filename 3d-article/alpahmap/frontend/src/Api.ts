import axios from "axios";
import type { Article } from "./Models";

class Api {
  private backendServer = axios.create({
    baseURL: "http://localhost:8080",
  });

  fetchArticles = async (): Promise<Article[]> => {
    const { data } = await this.backendServer.get("/article");
    return data;
  };

  fetchArticleModel = async (modelId: number): Promise<ArrayBuffer> => {
    const { data } = await this.backendServer.get(`/article/model/${modelId}`, {
      responseType: "arraybuffer",
    });
    return data;
  };
}

const api = new Api();

export default api;
