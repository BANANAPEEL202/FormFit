import { useState } from 'react';
import { AppPage } from './AppPage';
import { LandingPage } from './LandingPage';

export const Page = () => {
	const [isApp, setIsApp] = useState(false);

	return <>{isApp ? <AppPage /> : <LandingPage setIsApp={setIsApp} />}</>;
};
