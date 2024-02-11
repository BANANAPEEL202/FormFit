import { Dispatch, SetStateAction, useEffect, useState } from 'react';
import { Container, Title, Text, Button } from '@mantine/core';
import classes from './HeroImageRight.module.css';
import { Transition } from '@mantine/core';
export const LandingPage = ({
	setIsApp,
}: {
	setIsApp: Dispatch<SetStateAction<boolean>>;
}) => {
	const [animate, setAnmimate] = useState(false);

	useEffect(() => {
		setAnmimate(true);
	}, []);

	return (
		<div className={classes.root}>
			<Container size='lg'>
				<div className={classes.inner}>
					<div className={classes.content}>
						<Title className={classes.title}>
							{/* A{' '} */}
							<Text
								component='span'
								inherit
								variant='gradient'
								gradient={{ from: '#EE4266', to: 'blue' }}
							>
								FormFit
							</Text>{' '}
							{/* React components library */}
						</Title>

						<Transition
							mounted={animate}
							transition='fade'
							duration={1200}
							timingFunction='ease'
						>
							{(styles) => (
								<Text className={classes.description} style={{ ...styles, color: 'white' }} mt={30}>
									Unlock the secret to perfecting your workout technique with
									FormFit. Upload a video of your exercise routine, and let our
									cutting-edge technology analyze it against the ideal form.
									Receive personalized feedback and pinpoint areas for
									improvement to maximize your gains while minimizing the risk
									of injury. Elevate your fitness journey with FormFit - because
									precision makes perfection. Start optimizing your form today!
								</Text>
							)}
						</Transition>

						<Button
							variant='gradient'
							gradient={{ from: '#EE4266', to: 'blue' }}
							size='xl'
							className={classes.control}
							mt={40}
							onClick={() => setIsApp(true)}
						>
							Get started
						</Button>
					</div>
				</div>
			</Container>
		</div>
	);
};
