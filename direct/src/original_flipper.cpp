// Generated verbatim from vendored TFlipperEdge.cpp. See vendor/LICENSE.
#include "flipper.h"

float TFlipperEdge::FindCollisionDistance(const ray_type& ray)
{
	ray_type dstRay{};
	if (ControlPointDirtyFlag)
		set_control_points(CurrentAngle);
	auto distance = maths::distance_to_flipper(this, ray, dstRay);
	if (distance >= 1e9f)
		return 1e9f;

	NextBallPosition = dstRay.Origin;
	CollisionDirection = dstRay.Direction;
	return distance;
}

void TFlipperEdge::EdgeCollision(TBall* ball, float distance)
{
	if (FlipperFlag == MessageCode::TFlipperNull)
	{
		maths::basic_collision(
			ball,
			&NextBallPosition,
			&CollisionDirection,
			Elasticity,
			Smoothness,
			1e9f,
			0);
		return;
	}

	vector2 t1NextPos{NextBallPosition.X - T1.X, NextBallPosition.Y - T1.Y},
	        t1RotOrigin{RotOrigin.X - T1.X, RotOrigin.Y - T1.Y};
	auto crossProduct = maths::cross(t1RotOrigin, t1NextPos);

	bool frontCollision = false;
	if (crossProduct <= 0)
	{
		if (AngleMax > 0)
			frontCollision = true;
	}
	else if (AngleMax <= 0)
	{
		frontCollision = true;
	}

	if (FlipperFlag == MessageCode::TFlipperRetract)
	{
		frontCollision ^= true;
		CollisionLinePerp = LineB.PerpendicularC;
	}
	else
	{
		CollisionLinePerp = LineA.PerpendicularC;
	}

	auto dx = NextBallPosition.X - RotOrigin.X;
	auto dy = NextBallPosition.Y - RotOrigin.Y;
	auto distanceSq = dy * dy + dx * dx;
	if (frontCollision)
	{
		float boost = 0;
		if (circlebase.RadiusSq * 1.01f < distanceSq)
		{
			auto v21 = std::fabs(MoveSpeed) * std::sqrt(distanceSq / DistanceDivSq);
			auto dot1 = maths::DotProduct(CollisionLinePerp, CollisionDirection);
			if (dot1 >= 0)
				boost = CollisionMult * dot1 * v21;
		}

		auto threshold = boost <= 0.0f ? 1e9f : -1.0f;
		maths::basic_collision(
			ball,
			&NextBallPosition,
			&CollisionDirection,
			Elasticity,
			Smoothness,
			threshold,
			boost);
	}
	else
	{
		auto elasticity = Elasticity;
		if (circlebase.RadiusSq * 1.01f < distanceSq)
			elasticity = (1.0f - std::sqrt(distanceSq / DistanceDivSq)) * Elasticity;
		maths::basic_collision(ball, &NextBallPosition, &CollisionDirection, elasticity, Smoothness, 1e9f, 0.0);
	}
}

void TFlipperEdge::set_control_points(float angle)
{
	float sin, cos;
	maths::SinCos(angle, sin, cos);
	A1 = A1Src;
	A2 = A2Src;
	B1 = B1Src;
	B2 = B2Src;
	T1 = T1Src;
	maths::RotatePt(A1, sin, cos, RotOrigin);
	maths::RotatePt(A2, sin, cos, RotOrigin);
	maths::RotatePt(T1, sin, cos, RotOrigin);
	maths::RotatePt(B1, sin, cos, RotOrigin);
	maths::RotatePt(B2, sin, cos, RotOrigin);
	maths::line_init(LineA, A1.X, A1.Y, A2.X, A2.Y);
	maths::line_init(LineB, B1.X, B1.Y, B2.X, B2.Y);
	circlebase = {RotOrigin, CirclebaseRadiusSq};
	circleT1 = {T1, CircleT1RadiusSq};
	ControlPointDirtyFlag = false;
}

float TFlipperEdge::flipper_angle_delta(float timeDelta)
{
	if (FlipperFlag == MessageCode::TFlipperNull)
		return 0.0f;

	const auto deltaAngle = MoveSpeed * timeDelta;
	if (std::fabs(deltaAngle) > AngleRemainder)
		return AngleDst - CurrentAngle;
	return deltaAngle;
}

int TFlipperEdge::SetMotion(MessageCode code)
{
	switch (code)
	{
	case MessageCode::TFlipperExtend:
		AngleRemainder = std::fabs(AngleMax - CurrentAngle);
		AngleDst = AngleMax;
		MoveSpeed = ExtendSpeed;
		break;
	case MessageCode::TFlipperRetract:
		AngleRemainder = std::fabs(CurrentAngle);
		AngleDst = 0.0f;
		MoveSpeed = RetractSpeed;
		break;
	case MessageCode::Reset:
		AngleRemainder = 0.0f;
		AngleDst = 0.0f;
		break;
	default: break;
	}

	if (AngleRemainder == 0.0f)
		code = MessageCode::TFlipperNull;

	FlipperFlag = code;
	return static_cast<int>(code);
}
