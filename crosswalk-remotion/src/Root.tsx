import React from 'react';
import { Composition } from 'remotion';
import { InstagramCarousel } from './compositions/InstagramCarousel';
import { TikTokReel } from './compositions/TikTokReel';
import { LinkedInVideo } from './compositions/LinkedInVideo';
import { QuizResultVideo } from './compositions/QuizResultVideo';
import { FearExplainer } from './compositions/FearExplainer';
import { CrosswalkMethodExplainer } from './compositions/CrosswalkMethodExplainer';
import { AIBridgeExplainer } from './compositions/AIBridgeExplainer';
import { GriefExplainer } from './compositions/GriefExplainer';
import { NervousSystemExplainer } from './compositions/NervousSystemExplainer';
import { SelfDoubtExplainer } from './compositions/SelfDoubtExplainer';
import { CanadaDoctorsExplainer } from './compositions/CanadaDoctorsExplainer';
import { AvoidanceLoopExplainer } from './compositions/AvoidanceLoopExplainer';
import { BurnoutHabitsExplainer } from './compositions/BurnoutHabitsExplainer';
import { AprilPost } from './compositions/AprilPost';
import { LinkedInBanner } from './compositions/LinkedInBanner';
import { LinkedInPost } from './compositions/LinkedInPost';
import { EmailSignatureBanner } from './compositions/EmailSignatureBanner';
import { VideoOverlay } from './compositions/VideoOverlay';
import { CrosswalkHero } from './compositions/CrosswalkHero';
import { StoryReel } from './compositions/StoryReel';
import { APRIL_POSTS } from './data/april-posts';
import { MARCH_POSTS } from './data/march-posts';

// VideoOverlay: 15s × 30fps = 450 frames, 1080×1080
const VO_FRAMES = 450;

// Carousel durations: 7 slides × 90 frames each = 630 frames
const CAROUSEL_SLIDES = 7;
const SLIDE_FRAMES = 90;

// TikTok: longest script approx ~1300 frames — compute dynamically but set generous max
const TIKTOK_FRAMES = 1380;

// LinkedIn: longest post ~8 blocks × avg 80 = 640 frames
const LINKEDIN_FRAMES = 720;

// Quiz result: ~ctaStart (~200) + outro (~60) = ~320 frames
const QUIZ_FRAMES = 380;

export const RemotionRoot: React.FC = () => (
  <>
    {/* ── Story Reel — "The Morning Nobody Knew My Name" ── */}
    <Composition
      id="StoryReel-MorningNobodyKnewMyName"
      component={StoryReel}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />

    {/* ── Website Hero ── */}
    <Composition
      id="CrosswalkHero"
      component={CrosswalkHero}
      durationInFrames={300}
      fps={30}
      width={1920}
      height={1080}
    />

    {/* ── Instagram Carousels ── */}
    <Composition
      id="InstagramCarousel-MDtoCrossingGuard"
      component={InstagramCarousel}
      durationInFrames={CAROUSEL_SLIDES * SLIDE_FRAMES}
      fps={30}
      width={1080}
      height={1080}
      defaultProps={{ carouselId: 'md-to-crossing-guard' }}
    />
    <Composition
      id="InstagramCarousel-NotYourJobTitle"
      component={InstagramCarousel}
      durationInFrames={CAROUSEL_SLIDES * SLIDE_FRAMES}
      fps={30}
      width={1080}
      height={1080}
      defaultProps={{ carouselId: 'not-your-job-title' }}
    />
    <Composition
      id="InstagramCarousel-NobodyTellsYou"
      component={InstagramCarousel}
      durationInFrames={CAROUSEL_SLIDES * SLIDE_FRAMES}
      fps={30}
      width={1080}
      height={1080}
      defaultProps={{ carouselId: 'nobody-tells-you' }}
    />
    <Composition
      id="InstagramCarousel-FiveFears"
      component={InstagramCarousel}
      durationInFrames={CAROUSEL_SLIDES * SLIDE_FRAMES}
      fps={30}
      width={1080}
      height={1080}
      defaultProps={{ carouselId: 'five-fears-inside-cant-leave' }}
    />
    <Composition
      id="InstagramCarousel-FourStages"
      component={InstagramCarousel}
      durationInFrames={CAROUSEL_SLIDES * SLIDE_FRAMES}
      fps={30}
      width={1080}
      height={1080}
      defaultProps={{ carouselId: 'four-stages-of-stuck' }}
    />
    <Composition
      id="InstagramCarousel-SunkCostTrap"
      component={InstagramCarousel}
      durationInFrames={6 * SLIDE_FRAMES}
      fps={30}
      width={1080}
      height={1080}
      defaultProps={{ carouselId: 'sunk-cost-trap' }}
    />

    {/* ── LinkedIn Banner (static PNG export) ── */}
    <Composition
      id="LinkedInBanner"
      component={LinkedInBanner}
      durationInFrames={1}
      fps={30}
      width={1584}
      height={396}
    />

    {/* ── LinkedIn Post Images (static PNG export) ── */}
    <Composition
      id="LinkedInPost-SunkCostTrap"
      component={LinkedInPost}
      durationInFrames={1}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ postId: 'sunk-cost-trap' }}
    />

    {/* ── Email Signature Banner (static PNG export) ── */}
    <Composition
      id="EmailSignatureBanner"
      component={EmailSignatureBanner}
      durationInFrames={1}
      fps={30}
      width={600}
      height={150}
    />

    {/* ── TikTok / Reels ── */}
    <Composition
      id="TikTokReel-POVDoctorCrossingGuard"
      component={TikTokReel}
      durationInFrames={TIKTOK_FRAMES}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'pov-doctor-crossing-guard' }}
    />
    <Composition
      id="TikTokReel-PsychiatristStory"
      component={TikTokReel}
      durationInFrames={TIKTOK_FRAMES}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'psychiatrist-story' }}
    />
    <Composition
      id="TikTokReel-ThingsPeopleSay"
      component={TikTokReel}
      durationInFrames={TIKTOK_FRAMES}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'things-people-say' }}
    />
    <Composition
      id="TikTokReel-YellowVest"
      component={TikTokReel}
      durationInFrames={TIKTOK_FRAMES}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'yellow-vest' }}
    />
    <Composition
      id="TikTokReel-FearAuditWalkthrough"
      component={TikTokReel}
      durationInFrames={TIKTOK_FRAMES}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'fear-audit-walkthrough' }}
    />
    <Composition
      id="TikTokReel-FearKeepsPhysiciansStuck"
      component={TikTokReel}
      durationInFrames={1380}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'fear-keeps-physicians-stuck' }}
    />
    <Composition
      id="TikTokReel-IThoughtIWasAfraidOfFailing"
      component={TikTokReel}
      durationInFrames={TIKTOK_FRAMES}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'i-thought-i-was-afraid-of-failing' }}
    />
    <Composition
      id="TikTokReel-TheQuestionNobodyAsks"
      component={TikTokReel}
      durationInFrames={TIKTOK_FRAMES}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'the-question-nobody-asks' }}
    />
    <Composition
      id="TikTokReel-EveryonesSafePlace"
      component={TikTokReel}
      durationInFrames={1500}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'everyone-elses-safe-place' }}
    />
    <Composition
      id="TikTokReel-FearAuditInstagram"
      component={TikTokReel}
      durationInFrames={1800}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'fear-audit-instagram' }}
    />

    {/* ── Fear Audit Reel (5-scene 60s) ── */}
    <Composition
      id="TikTokReel-fear-audit"
      component={TikTokReel}
      durationInFrames={1800}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ scriptId: 'fear-audit' }}
    />

    {/* ── LinkedIn Videos ── */}
    <Composition
      id="LinkedInVideo-SunkCost"
      component={LinkedInVideo}
      durationInFrames={LINKEDIN_FRAMES}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ postId: 'sunk-cost' }}
    />
    <Composition
      id="LinkedInVideo-WhatWillPeopleThink"
      component={LinkedInVideo}
      durationInFrames={LINKEDIN_FRAMES}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ postId: 'what-will-people-think' }}
    />
    <Composition
      id="LinkedInVideo-QuittingIsNotFailure"
      component={LinkedInVideo}
      durationInFrames={LINKEDIN_FRAMES}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ postId: 'quitting-is-not-failure' }}
    />
    <Composition
      id="LinkedInVideo-FearAuditIntro"
      component={LinkedInVideo}
      durationInFrames={LINKEDIN_FRAMES}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ postId: 'fear-audit-intro' }}
    />
    <Composition
      id="LinkedInVideo-NamingFear"
      component={LinkedInVideo}
      durationInFrames={LINKEDIN_FRAMES}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ postId: 'naming-fear' }}
    />
    <Composition
      id="LinkedInVideo-FiveFears"
      component={LinkedInVideo}
      durationInFrames={LINKEDIN_FRAMES}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ postId: 'five-fears' }}
    />
    <Composition
      id="LinkedInVideo-FourStages"
      component={LinkedInVideo}
      durationInFrames={LINKEDIN_FRAMES}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ postId: 'four-stages' }}
    />
    <Composition
      id="LinkedInVideo-WhyIBuiltIt"
      component={LinkedInVideo}
      durationInFrames={LINKEDIN_FRAMES}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ postId: 'why-i-built-it' }}
    />

    {/* ── Quiz Result Videos — all 4 stages, square + vertical ── */}
    {/* ── Educational Explainers ── */}
    <Composition
      id="CanadaDoctorsExplainer-CanadaDoctors"
      component={CanadaDoctorsExplainer}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="BurnoutHabitsExplainer-BurnoutHabits"
      component={BurnoutHabitsExplainer}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="FearExplainer-TheFear"
      component={FearExplainer}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="CrosswalkMethodExplainer"
      component={CrosswalkMethodExplainer}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="AIBridgeExplainer"
      component={AIBridgeExplainer}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="GriefExplainer"
      component={GriefExplainer}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="NervousSystemExplainer-NervousSystem"
      component={NervousSystemExplainer}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="SelfDoubtExplainer-SelfDoubt"
      component={SelfDoubtExplainer}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="AvoidanceLoopExplainer-AvoidanceLoop"
      component={AvoidanceLoopExplainer}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />

    {(['START', 'STOP', 'ELDER', 'HUMAN'] as const).map((stage) => (
      <React.Fragment key={stage}>
        <Composition
          id={`QuizResult-${stage}-Square`}
          component={QuizResultVideo}
          durationInFrames={QUIZ_FRAMES}
          fps={30}
          width={1080}
          height={1080}
          defaultProps={{ stage, format: 'square' }}
        />
        <Composition
          id={`QuizResult-${stage}-Vertical`}
          component={QuizResultVideo}
          durationInFrames={QUIZ_FRAMES}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={{ stage, format: 'vertical' }}
        />
      </React.Fragment>
    ))}

    {/* ── March 26–31 + May 1 Posts — animated reels (1080×1920, 8s each) ── */}
    {MARCH_POSTS.map((post) => (
      <Composition
        key={post.slug}
        id={`AprilPost-${post.slug}`}
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        component={AprilPost as any}
        durationInFrames={240}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ postId: post.slug }}
      />
    ))}

    {/* ── April 2026 Posts — 30 animated reels (1080×1920, 8s each) ── */}
    {APRIL_POSTS.map((post) => (
      <Composition
        key={post.slug}
        id={`AprilPost-${post.slug}`}
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        component={AprilPost as any}
        durationInFrames={240}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ postId: post.slug }}
      />
    ))}

    {/* ── Video Overlays — 17 social posts (1080×1080, 15s) ── */}
    {[
      '01-sunk-cost',
      '02-what-will-people-think',
      '03-quitting',
      '04-fear-audit-intro',
      '05-named-fear',
      '06-five-fears',
      '07-four-stages',
      '09-why-i-built-it',
      '10-psychiatrist',
      '11-phone-call',
      '12-yellow-vest',
      '13-loneliest',
      '14-3am',
      '15-take-it-personally',
      '16-first-step',
      '17-what-do-you-do',
      '18-courage',
    ].map((id) => (
      <Composition
        key={id}
        id={`VideoOverlay-${id}`}
        component={VideoOverlay}
        durationInFrames={VO_FRAMES}
        fps={30}
        width={1080}
        height={1080}
        defaultProps={{ overlayId: id }}
      />
    ))}
  </>
);
