import type { Object3D } from "three";

export interface Article {
  id: number;
  title: string;
  content: string;
  imageUrl: string;
  model: Model;
}

export interface Model {
  id: number;
  filename: string;
  filepath: string;
  latitude: number;
  longitude: number;
  height: number;
  scale: number;
  object3D?: Object3D;
}

export interface MessageInterface {
  message: string;
}

export interface Message extends MessageInterface {
  role: "user" | "model";
}
