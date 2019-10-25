package cn.nubia.ui;

import android.graphics.PointF;

/**
 * Created by Administrator on 2019/10/25.
 */

public class CircleUtils {

    public static PointF[] getTangentPoints(PointF c1, float r1, PointF c2, float r2){
        float centerLine = (float) Math.sqrt(Math.pow(c1.x-c2.x,2)+Math.pow(c1.y-c2.y, 2));
        if(centerLine > r1+r2){
            //计算内切
            PointF[] points = new PointF[5];
            //内切线焦点
            points[0] = new PointF((c1.x*r2+c2.x*r1)/(r1+r2), (c1.y*r2+c2.y*r1)/(r1+r2));
            float l1 = centerLine*r1/(r1+r2);
            float l2 = centerLine*r2/(r1+r2);
            //圆心连线与圆1的交点
            PointF internalPoint = internalPoint(c1, points[0], r1/l1);
            float angle = (float) Math.acos(r1/l1);
            //第1个圆的切点
            points[1] = rotate(internalPoint, c1, angle);
            points[2] = rotate(internalPoint, c1, -angle);
            //圆心连线与圆2的交点
            internalPoint = internalPoint(points[0], c2, (l2-r2)/l2);
            //第2个圆的切点
            points[3] = rotate(internalPoint, c2, -angle);
            points[4] = rotate(internalPoint, c2, angle);
            return points;
        }else {
            //计算外切
            PointF[] points = new PointF[6];
            //圆心连线与圆1的交点
            PointF internalPoint1 = internalPoint(c1, c2, r1/centerLine);
            //圆心连线与圆2的交点
            PointF internalPoint2 = internalPoint(c1, c2, (centerLine-r2)/centerLine);
            //两元交点连线和两圆焦点在左边圆的角度
            float angleR1 = (float) Math.acos((r1*r1+centerLine*centerLine-r2*r2)/(2*r1*centerLine));
            //两元交点连线和两圆焦点在右边圆的角度
            float angleR2 = (float) Math.acos((r2*r2+centerLine*centerLine-r1*r1)/(2*r2*centerLine));
            //外切线与圆心连线的角度(0~90度之间的角度)
            float angle = (float) Math.acos(Math.abs(r1-r2)/centerLine);
            //两圆的交点
            points[0] = rotate(internalPoint1, c1, angleR1);
            points[3] = rotate(internalPoint2, c2, angleR2);
            if(r1>=r2){
                //切线与第一个圆的交点
                points[1] = rotate(internalPoint1, c1, angle);
                points[2] = rotate(internalPoint1, c1, -angle);
                //切线与第二个圆的交点
                points[4] = rotate(internalPoint2, c2, -(float) (Math.PI-angle));
                points[5] = rotate(internalPoint2, c2, (float) (Math.PI-angle));
            }else{
                //切线与第一个圆的交点
                points[1] = rotate(internalPoint1, c1, (float) (Math.PI-angle));
                points[2] = rotate(internalPoint1, c1, -(float) (Math.PI-angle));
                //切线与第二个圆的交点
                points[4] = rotate(internalPoint2, c2, -angle);
                points[5] = rotate(internalPoint2, c2, angle);
            }
            return points;
        }
    }

    public static PointF internalPoint(PointF startPoint, PointF endPoint, float ratio){
        if(startPoint == null){
            startPoint = new PointF(0, 0);
        }
        PointF ret = new PointF();
        float x = endPoint.x-startPoint.x;
        float y = endPoint.y-startPoint.y;
        ret.x = x*ratio+startPoint.x;
        ret.y = y*ratio+startPoint.y;
        return ret;
    }

    public static PointF rotate(PointF point, PointF center, float angle){
        if(center == null){
            center = new PointF(0, 0);
        }
        PointF ret = new PointF();
        float x = point.x-center.x;
        float y = point.y-center.y;
        ret.x = (float) ((x*Math.cos(angle)-y*Math.sin(angle))+center.x);
        ret.y = (float) ((x*Math.sin(angle)+y*Math.cos(angle))+center.y);
        return ret;
    }
}
