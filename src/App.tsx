import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/dropzone/styles.css';
import { MantineProvider } from '@mantine/core';
import { theme } from './theme';
import { Notifications } from '@mantine/notifications';
import { ModalsProvider } from '@mantine/modals';
import { Page } from './Page';

export default function App() {
	return (
		<MantineProvider theme={theme} forceColorScheme='dark'>
			<ModalsProvider>
				<Notifications />
				<Page />
			</ModalsProvider>
		</MantineProvider>
	);
}
