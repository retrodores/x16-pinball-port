#pragma once
#include "port_types.h"
enum class MessageCode
{
	// Private codes <1000, different meaning for each component
	TFlipperNull = 0,
	TFlipperExtend = 1,
	TFlipperRetract = 2,

	TLightTurnOff = 0,
	TLightTurnOn = 1,
	TLightGetLightOnFlag = 2,
	TLightGetFlasherOnFlag = 3,
	TLightFlasherStart = 4,
	TLightApplyMultDelay = 5,
	TLightApplyDelay = 6,
	TLightFlasherStartTimed = 7,
	TLightTurnOffTimed = 8,
	TLightTurnOnTimed = 9,
	TLightSetOnStateBmpIndex = 11,
	TLightIncOnStateBmpIndex = 12,
	TLightDecOnStateBmpIndex = 13,
	TLightResetTimed = 14,
	TLightFlasherStartTimedThenStayOn = 15,
	TLightFlasherStartTimedThenStayOff = 16,
	TLightToggleValue = 17,
	TLightResetAndToggleValue = 18,
	TLightResetAndTurnOn = 19,
	TLightResetAndTurnOff = 20,
	TLightToggle = 21,
	TLightResetAndToggle = 22,
	TLightSetMessageField = 23,
	TLightFtTmpOverrideOn = -24,
	TLightFtTmpOverrideOff = -25,
	TLightFtResetOverride = -26,

	TLightGroupNull = 0,
	TLightGroupStepBackward = 24,
	TLightGroupStepForward = 25,
	TLightGroupAnimationBackward = 26,
	TLightGroupAnimationForward = 27,
	TLightGroupLightShowAnimation = 28,
	TLightGroupGameOverAnimation = 29,
	TLightGroupRandomAnimationSaturation = 30,
	TLightGroupRandomAnimationDesaturation = 31,
	TLightGroupOffsetAnimationForward = 32,
	TLightGroupOffsetAnimationBackward = 33,
	TLightGroupReset = 34,
	TLightGroupTurnOnAtIndex = 35,
	TLightGroupTurnOffAtIndex = 36,
	TLightGroupGetOnCount = 37,
	TLightGroupGetLightCount = 38,
	TLightGroupGetMessage2 = 39,
	TLightGroupGetAnimationFlag = 40,
	TLightGroupResetAndTurnOn = 41,
	TLightGroupResetAndTurnOff = 42,
	TLightGroupRestartNotifyTimer = 43,
	TLightGroupFlashWhenOn = 44,
	TLightGroupToggleSplitIndex = 45,
	TLightGroupStartFlasher = 46,
	TLightGroupCountdownEnded = 47,

	TBumperSetBmpIndex = 11,
	TBumperIncBmpIndex = 12,
	TBumperDecBmpIndex = 13,

	TComponentGroupResetNotifyTimer = 48,

	TPopupTargetDisable = 49,
	TPopupTargetEnable = 50,

	TBlockerDisable = 51,
	TBlockerEnable = 52,
	TBlockerRestartTimeout = 59,

	TGateDisable = 53,
	TGateEnable = 54,

	TKickoutRestartTimer = 55,

	TSinkUnknown7 = 7,
	TSinkResetTimer = 56,

	TSoloTargetDisable = 49,
	TSoloTargetEnable = 50,

	TTimerResetTimer = 59,

	ControlBallCaptured = 57,
	ControlBallReleased = 58,
	ControlTimerExpired = 60,
	ControlNotifyTimerExpired = 61,
	ControlSpinnerLoopReset = 62,
	ControlCollision = 63,
	ControlEnableMultiplier = 64,
	ControlDisableMultiplier = 65,
	ControlMissionComplete = 66,
	ControlMissionStarted = 67,

	// Public codes 1000+, apply to all components
	LeftFlipperInputPressed = 1000,
	LeftFlipperInputReleased = 1001,
	RightFlipperInputPressed = 1002,
	RightFlipperInputReleased = 1003,
	PlungerInputPressed = 1004,
	PlungerInputReleased = 1005,
	Pause = 1008,
	Resume = 1009,
	LooseFocus = 1010,
	SetTiltLock = 1011,
	ClearTiltLock = 1012,
	StartGamePlayer1 = 1013,
	NewGame = 1014,
	PlungerFeedBall = 1015,
	PlungerStartFeedTimer = 1016,
	PlungerLaunchBall = 1017,
	PlungerRelaunchBall = 1018,
	PlayerChanged = 1020,
	SwitchToNextPlayer = 1021,
	GameOver = 1022,
	Reset = 1024,
};
// Platform shell: original physics state and method bodies, without SDL ownership.
class TFlipperEdge {
public:
 uint16_t CollisionGroup=1;
 float FindCollisionDistance(const ray_type& ray);
 void EdgeCollision(TBall* ball,float distance);
 void set_control_points(float angle);
 float flipper_angle_delta(float timeDelta);
 int SetMotion(MessageCode code);
	MessageCode FlipperFlag{};
	float Elasticity;
	float Smoothness;
	vector2 RotOrigin{};
	float CirclebaseRadius;
	float CircleT1Radius;
	float CirclebaseRadiusSq;
	float CircleT1RadiusSq;
	float CirclebaseRadiusMSq;
	float CircleT1RadiusMSq;
	float AngleMax;
	float AngleRemainder{};
	float AngleDst;
	float CurrentAngle{};
	vector2 CollisionLinePerp{};
	vector2 A1Src{};
	vector2 A2Src{};
	vector2 B1Src{};
	vector2 B2Src{};
	float CollisionMult;
	vector2 T1Src{};
	vector2 T2Src{};
	float DistanceDiv, DistanceDivSq;
	vector2 CollisionDirection{};
	float ExtendSpeed;
	float RetractSpeed;
	float MoveSpeed;
	vector2 NextBallPosition{};
	vector2 A1, A2, B1, B2, T1;
	line_type LineA, LineB;
	circle_type circlebase, circleT1;
	float InvT1Radius;
	float YMin, YMax, XMin, XMax;
	bool ControlPointDirtyFlag{};
};
// Single-ball native ownership adapter; physics method bodies stay unchanged.
class TFlipper {
public:
 TFlipperEdge* FlipperEdge;
 int MessageField=0;
 int GetFlipperStepAngle(float dt,float* dst) const;
 void FlipperCollision(float deltaAngle);
};
struct NativeTable {
 TBall* BallList[1];
 vector2 PlungerPosition{};
 float CollisionCompOffset=.3f;
 bool TiltLockFlag=false;
 unsigned MultiballCount=0;
 unsigned BallInDrainFlag=0;
 int BallCountInRect(const vector2& pos,float margin);
 TBall* AddBall(vector2 position);
};
namespace pb {extern NativeTable* MainTable; extern bool FullTiltMode; void tilt_no_more();}
namespace flippers {
extern TFlipperEdge edges[2];
extern unsigned short contacts;
void reset();
void set(unsigned char index,bool pressed);
int steps(unsigned char index,float dt,float& delta);
void advance(unsigned char index,float delta,TBall& ball);
float nearest(const ray_type& ray,unsigned char& index);
}
