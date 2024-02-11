import {
	Accordion,
	Button,
	Center,
	Group,
	Loader,
	Paper,
	Select,
	Stack,
	Text,
	Title,
	rem,
} from '@mantine/core';
import { Dropzone, FileWithPath, MIME_TYPES } from '@mantine/dropzone';
import { notifications } from '@mantine/notifications';
import './backApp.css';
import {
	IconCheck,
	IconDownload,
	IconPhoto,
	IconReload,
	IconUpload,
	IconX,
} from '@tabler/icons-react';
import { useRef, useState } from 'react';

const OUTPUT_MIME = 'video/mp4';
const OUTPUT_EXT = '.mp4';
const BACKEND_URI = import.meta.env.DEV
	? `http://localhost:8000`
	: 'https://backend-3u3ymdcitq-ue.a.run.app';

const MB = 1024 ** 2;

const isValidExerciseNumber = (num: string): boolean =>
	num === '0' || num === '1' || num === '2';

const numToExercise = (num: string) => {
	if (num === '0') return 'Squat';
	if (num === '1') return 'Lunge';
	if (num === '2') return 'Push-Up';
	throw new Error(`Invalid exercise num ${num}`);
};

export const AppPage = () => {
	const [state, setState] = useState<
		| { state: 'upload' }
		| { state: 'uploading' }
		| { state: 'analyzing'; id: string }
		| {
				state: 'result';
				id: string;
				feedback: { name: string; feedback: string; satisfactory: boolean }[];
				video: string;
		  }
	>({ state: 'upload' });
	const [exercise, setExercise] = useState('0');
	const [video, setVideo] = useState<FileWithPath | undefined>(undefined);
	const videoRef = useRef<HTMLVideoElement>(null);
	const sse = useRef<EventSource | undefined>();

	return (
		<div className='backgroundImage'>
			<Center style={{ width: '100%', height: '100%' }}>
				{state.state === 'upload' || state.state === 'uploading' ? (
					<Stack align='center' justify='center'>
						<div className='addName'>
							<Title>Add Your Video</Title>
						</div>
						<Select
							label='Choose Your Exercise'
							value={exercise}
							onChange={(v) => setExercise(v ?? '0')}
							data={[
								{
									group: 'Legs 🦵',
									items: [
										{
											label: 'Squats 🏋️‍♀️',
											value: '0',
										},
										{
											label: 'Lunges',
											value: '1',
										},
									],
								},
								{
									group: 'Arms 💪',
									items: [
										{
											label: 'Push-Ups',
											value: '2',
										},
									],
								},
							]}
						/>
						<Dropzone
							className='uploadBox'
							onDrop={(files) => {
								if (files[0]) {
									setVideo(files[0]);
									notifications.show({
										icon: (
											<IconCheck style={{ width: rem(18), height: rem(18) }} />
										),
										color: '#4186d9',
										title: 'Ready!',
										autoClose: 4_000,
										message: 'Ready to upload video!',
									});
								}
							}}
							onReject={(files) => console.log('Rejected files:', files)}
							maxSize={50 * MB}
							accept={[MIME_TYPES.mp4, 'video/quicktime']}
						>
							<Group
								justify='center'
								gap='xl'
								mih={220}
								style={{ pointerEvents: 'none' }}
							>
								<Dropzone.Accept>
									<IconUpload
										style={{
											width: rem(52),
											height: rem(52),
											color: 'var(--mantine-color-blue-6)',
										}}
										stroke={1.5}
									/>
								</Dropzone.Accept>
								<Dropzone.Reject>
									<IconX
										style={{
											width: rem(52),
											height: rem(52),
											color: 'var(--mantine-color-red-6)',
										}}
										stroke={1.5}
									/>
								</Dropzone.Reject>
								<Dropzone.Idle>
									<IconPhoto
										style={{
											width: rem(52),
											height: rem(52),
											color: 'var(--mantine-color-dimmed)',
										}}
										stroke={1.5}
									/>
								</Dropzone.Idle>

								<div>
									<Text className='dragText' size='xl' inline>
										Drag video here or click to select file
									</Text>
									<Text className='sizeLimit' size='m' c='dimmed' inline mt={7}>
										Video should not exceed 50mb
									</Text>
								</div>
							</Group>
						</Dropzone>
						<Button
							className='button'
							loading={state.state === 'uploading'}
							disabled={!video}
							leftSection={
								<IconUpload style={{ width: rem(16), height: rem(16) }} />
							}
							onClick={async () => {
								setState({ state: 'uploading' });
								if (!isValidExerciseNumber(exercise)) {
									notifications.show({
										icon: <IconX style={{ width: rem(18), height: rem(18) }} />,
										color: 'red',
										title: 'Error',
										autoClose: 10_000,
										message: 'Invalid Exercise Selected! D:',
									});
									return;
								}
								if (!video) {
									setState({ state: 'upload' });
									return;
								}

								const res = await fetch(
									BACKEND_URI + `/upload?exercise=${exercise}`,
									{
										body: video,
										method: 'POST',
										headers: {
											['content-type']: video.type,
										},
									}
								);

								if (res.ok) {
									const { id } = (await res.json()) as { id: string };

									sse.current = new EventSource(
										BACKEND_URI + `/wait-for-analyze/${id}`
									);

									sse.current.addEventListener('error', () => {
										notifications.show({
											icon: (
												<IconX style={{ width: rem(18), height: rem(18) }} />
											),
											color: 'red',
											title: 'Error',
											autoClose: 10_000,
											message: 'Error during SSE connection.',
										});
										sse.current?.close();
										sse.current = undefined;
										setState({ state: 'upload' });
									});

									sse.current.addEventListener('message', async (e) => {
										const data:
											| {
													result: 'success';
													feedback: {
														name: string;
														feedback: string;
														satisfactory: boolean;
													}[];
											  }
											| { result: 'fail'; message: string } = JSON.parse(
											e.data
										);

										if (data.result == 'fail') {
											sse.current?.close();
											sse.current = undefined;

											notifications.show({
												icon: (
													<IconX style={{ width: rem(18), height: rem(18) }} />
												),
												color: 'red',
												title: 'Error',
												autoClose: 10_000,
												message: data.message,
											});
											setState({ state: 'upload' });
										} else {
											// Close after receiving 1 message
											sse.current?.close();
											sse.current = undefined;

											const res = await fetch(BACKEND_URI + `/result/${id}`);

											if (res.ok) {
												const video = await res.blob();

												setState({
													state: 'result',
													id,
													feedback: data.feedback,
													video: URL.createObjectURL(video),
												});
											} else {
												notifications.show({
													icon: (
														<IconX
															style={{ width: rem(18), height: rem(18) }}
														/>
													),
													color: 'red',
													title: 'Error',
													autoClose: 10_000,
													message: 'Failed to download result video. D:',
												});
												setState({ state: 'upload' });
											}
										}
									});

									setState({ state: 'analyzing', id });
									return;
								}

								setState({ state: 'upload' });
							}}
						>
							Upload
						</Button>
					</Stack>
				) : state.state === 'analyzing' ? (
					<Stack align='center' justify='center'>
						<Loader size='xl' />
						<Text className='analyzingLoad' ta='center'>
							Analyzing your video with our advanced, powerful algorithms. 💪
						</Text>
						<Text c='dimmed' ta='center'>Video Id: {state.id}</Text>
					</Stack>
				) : state.state === 'result' ? (
					<Stack align='center' justify='center'>
						<Title className='analyzedVideo'>
							Your Video Has Been Analyzed!
						</Title>
						<Group justify='center' gap='xl'>
							<Paper p='md'>
								<Title order={2}>Your {numToExercise(exercise)} Feedback</Title>
								<Accordion maw={rem(270)}>
									{state.feedback
										.sort((a) => (a.satisfactory ? 1 : 0))
										.map((feedback) => (
											<Accordion.Item key={feedback.name} value={feedback.name}>
												<Accordion.Control
													disabled={feedback.satisfactory}
													styles={{
														label: {
															color: feedback.satisfactory
																? 'white'
																: undefined,
														},
														chevron: {
															display: feedback.satisfactory
																? 'none'
																: undefined,
														},
													}}
													icon={
														feedback.satisfactory ? (
															<IconCheck
																style={{ width: rem(16), height: rem(16) }}
																color='#4186d9'
															/>
														) : (
															<IconX
																style={{ width: rem(16), height: rem(16) }}
																color='red'
															/>
														)
													}
												>
													{feedback.name}
												</Accordion.Control>
												<Accordion.Panel>{feedback.feedback}</Accordion.Panel>
											</Accordion.Item>
										))}
								</Accordion>
							</Paper>
							<video height={360} ref={videoRef} controls>
								<source src={state.video} type={OUTPUT_MIME}></source>
							</video>
						</Group>
						<Group>
							<Button
								className='button'
								component='a'
								href={state.video}
								download={`${numToExercise(exercise)}-` + state.id + OUTPUT_EXT}
								leftSection={
									<IconDownload style={{ height: rem(16), width: rem(16) }} />
								}
							>
								Download
							</Button>
							<Button
								className='button'
								onClick={() => setState({ state: 'upload' })}
								leftSection={
									<IconReload style={{ height: rem(16), width: rem(16) }} />
								}
							>
								Restart
							</Button>
						</Group>
					</Stack>
				) : null}
			</Center>
		</div>
	);
};
