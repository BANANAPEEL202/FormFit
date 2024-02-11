/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly VITE_ENV: 'prod';
	// more env variables...
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}
