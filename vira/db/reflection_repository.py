"""
Self-reflection sistemi için veritabanı işlemleri.
Yansıtma oturumları, içgörüler ve hedefler için CRUD işlemleri.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from vira.db.engine import db_session
from vira.db.models import ReflectionSession, AutonomousInsight, EmergentGoal, User, LongTermMemory
from vira.utils.logger import get_logger

logger = get_logger(__name__)


class ReflectionRepository:
    """Self-reflection sistemi için veritabanı işlemleri"""
    
    def create_reflection_session(self, user_id: str, reflection_type: str,
                                 trigger_reasons: List[str] = None,
                                 analysis_results: Dict[str, Any] = None) -> Optional[str]:
        """
        Yansıtma oturumu oluştur ve kaydet
        
        Args:
            user_id: Kullanıcı ID'si
            reflection_type: Yansıtma türü ('daily', 'weekly', 'event_triggered', 'realtime', 'scheduled')
            trigger_reasons: Tetikleme nedenleri listesi
            analysis_results: Analiz sonuçları
            
        Returns:
            str: Oluşturulan oturum ID'si veya None
        """
        try:
            with db_session() as session:
                reflection_session = ReflectionSession(
                    user_id=user_id,
                    reflection_type=reflection_type,
                    trigger_reasons=trigger_reasons or [],
                    analysis_results=analysis_results or {},
                    insights_generated=0,
                    goals_created=0,
                    reflection_depth=0.5,
                    created_at=datetime.now()
                )
                
                session.add(reflection_session)
                session.flush()  # ID'yi almak için flush
                
                session_id = str(reflection_session.id)
                logger.info(f"Reflection session created: {session_id} for user {user_id}")
                return session_id
                
        except Exception as e:
            logger.error(f"Error creating reflection session: {str(e)}", exc_info=True)
            return None

    def create_insight(self, user_id: str, insight_text: str, insight_type: str,
                      confidence_score: float = 0.5, source_memory_ids: List[str] = None,
                      session_id: Optional[str] = None) -> Optional[str]:
        """
        İçgörü oluştur ve kaydet
        
        Args:
            user_id: Kullanıcı ID'si
            insight_text: İçgörü metni
            insight_type: İçgörü türü ('pattern_recognition', 'emotional_evolution', 'behavioral_change')
            confidence_score: Güven skoru (0.0-1.0)
            source_memory_ids: Kaynak hafıza ID'leri
            session_id: İlişkili yansıtma oturumu ID'si
            
        Returns:
            str: Oluşturulan içgörü ID'si veya None
        """
        try:
            with db_session() as session:
                insight = AutonomousInsight(
                    user_id=user_id,
                    insight_text=insight_text,
                    insight_type=insight_type,
                    confidence_score=confidence_score,
                    source_memory_ids=source_memory_ids or [],
                    created_at=datetime.now(),
                    acted_upon=False,
                    action_results={}
                )
                
                session.add(insight)
                session.flush()  # ID'yi almak için flush
                
                insight_id = str(insight.id)
                logger.info(f"Insight created: {insight_id} for user {user_id}")
                return insight_id
                
        except Exception as e:
            logger.error(f"Error creating insight: {str(e)}", exc_info=True)
            return None

    def create_goal(self, user_id: str, goal_text: str, goal_type: str,
                   priority: int = 5, source_insight_id: Optional[str] = None,
                   target_date: Optional[datetime] = None, session_id: Optional[str] = None) -> Optional[str]:
        """
        Hedef oluştur ve kaydet
        
        Args:
            user_id: Kullanıcı ID'si
            goal_text: Hedef metni
            goal_type: Hedef türü ('relationship_building', 'emotional_support', 'proactive_assistance')
            priority: Öncelik (1-10 arası)
            source_insight_id: Kaynak içgörü ID'si
            target_date: Hedef tarihi
            session_id: İlişkili yansıtma oturumu ID'si
            
        Returns:
            str: Oluşturulan hedef ID'si veya None
        """
        try:
            with db_session() as session:
                goal = EmergentGoal(
                    user_id=user_id,
                    goal_text=goal_text,
                    goal_type=goal_type,
                    priority=priority,
                    status='active',
                    source_insight_id=source_insight_id,
                    progress_metrics={},
                    created_at=datetime.now(),
                    target_date=target_date
                )
                
                session.add(goal)
                session.flush()  # ID'yi almak için flush
                
                goal_id = str(goal.id)
                logger.info(f"Goal created: {goal_id} for user {user_id}")
                return goal_id
                
        except Exception as e:
            logger.error(f"Error creating goal: {str(e)}", exc_info=True)
            return None

    def get_reflection_sessions(self, user_id: str, limit: int = 10, 
                               reflection_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Kullanıcının yansıtma oturumlarını getir
        
        Args:
            user_id: Kullanıcı ID'si
            limit: Maksimum kayıt sayısı
            reflection_type: Belirli bir yansıtma türü filtresi
            
        Returns:
            List[Dict]: Yansıtma oturumları listesi
        """
        try:
            with db_session() as session:
                query = session.query(ReflectionSession).filter(
                    ReflectionSession.user_id == user_id
                )
                
                if reflection_type:
                    query = query.filter(ReflectionSession.reflection_type == reflection_type)
                
                sessions = query.order_by(desc(ReflectionSession.created_at)).limit(limit).all()
                
                result = []
                for session_obj in sessions:
                    result.append({
                        'id': str(session_obj.id),
                        'user_id': str(session_obj.user_id),
                        'reflection_type': session_obj.reflection_type,
                        'trigger_reasons': session_obj.trigger_reasons,
                        'analysis_results': session_obj.analysis_results,
                        'insights_generated': session_obj.insights_generated,
                        'goals_created': session_obj.goals_created,
                        'reflection_depth': session_obj.reflection_depth,
                        'created_at': session_obj.created_at.isoformat() if session_obj.created_at else None,
                        'duration_seconds': session_obj.duration_seconds
                    })
                
                logger.debug(f"Retrieved {len(result)} reflection sessions for user {user_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error getting reflection sessions: {str(e)}", exc_info=True)
            return []

    def get_insights(self, user_id: str, limit: int = 20, 
                    insight_type: Optional[str] = None,
                    min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """
        Kullanıcının içgörülerini getir
        
        Args:
            user_id: Kullanıcı ID'si
            limit: Maksimum kayıt sayısı
            insight_type: Belirli bir içgörü türü filtresi
            min_confidence: Minimum güven skoru
            
        Returns:
            List[Dict]: İçgörüler listesi
        """
        try:
            with db_session() as session:
                query = session.query(AutonomousInsight).filter(
                    and_(
                        AutonomousInsight.user_id == user_id,
                        AutonomousInsight.confidence_score >= min_confidence
                    )
                )
                
                if insight_type:
                    query = query.filter(AutonomousInsight.insight_type == insight_type)
                
                insights = query.order_by(desc(AutonomousInsight.created_at)).limit(limit).all()
                
                result = []
                for insight in insights:
                    result.append({
                        'id': str(insight.id),
                        'user_id': str(insight.user_id),
                        'insight_text': insight.insight_text,
                        'insight_type': insight.insight_type,
                        'confidence_score': insight.confidence_score,
                        'source_memory_ids': insight.source_memory_ids,
                        'created_at': insight.created_at.isoformat() if insight.created_at else None,
                        'acted_upon': insight.acted_upon,
                        'action_results': insight.action_results
                    })
                
                logger.debug(f"Retrieved {len(result)} insights for user {user_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error getting insights: {str(e)}", exc_info=True)
            return []

    def get_active_goals(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Kullanıcının aktif hedeflerini getir
        
        Args:
            user_id: Kullanıcı ID'si
            limit: Maksimum kayıt sayısı
            
        Returns:
            List[Dict]: Aktif hedefler listesi
        """
        try:
            with db_session() as session:
                goals = session.query(EmergentGoal).filter(
                    and_(
                        EmergentGoal.user_id == user_id,
                        EmergentGoal.status == 'active'
                    )
                ).order_by(desc(EmergentGoal.priority), desc(EmergentGoal.created_at)).limit(limit).all()
                
                result = []
                for goal in goals:
                    result.append({
                        'id': str(goal.id),
                        'user_id': str(goal.user_id),
                        'goal_text': goal.goal_text,
                        'goal_type': goal.goal_type,
                        'priority': goal.priority,
                        'status': goal.status,
                        'source_insight_id': str(goal.source_insight_id) if goal.source_insight_id else None,
                        'progress_metrics': goal.progress_metrics,
                        'created_at': goal.created_at.isoformat() if goal.created_at else None,
                        'target_date': goal.target_date.isoformat() if goal.target_date else None,
                        'completion_date': goal.completion_date.isoformat() if goal.completion_date else None
                    })
                
                logger.debug(f"Retrieved {len(result)} active goals for user {user_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error getting active goals: {str(e)}", exc_info=True)
            return []

    def update_reflection_session(self, session_id: str, insights_generated: Optional[int] = None,
                                 goals_created: Optional[int] = None, 
                                 reflection_depth: Optional[float] = None,
                                 duration_seconds: Optional[int] = None,
                                 analysis_results: Optional[Dict[str, Any]] = None) -> bool:
        """
        Yansıtma oturumunu güncelle
        
        Args:
            session_id: Oturum ID'si
            insights_generated: Oluşturulan içgörü sayısı
            goals_created: Oluşturulan hedef sayısı
            reflection_depth: Yansıtma derinliği
            duration_seconds: Süre (saniye)
            analysis_results: Analiz sonuçları
            
        Returns:
            bool: Güncelleme başarılı mı
        """
        try:
            with db_session() as session:
                reflection_session = session.query(ReflectionSession).filter(
                    ReflectionSession.id == session_id
                ).first()
                
                if not reflection_session:
                    logger.warning(f"Reflection session not found: {session_id}")
                    return False
                
                # Sadece None olmayan değerleri güncelle
                if insights_generated is not None:
                    reflection_session.insights_generated = insights_generated
                if goals_created is not None:
                    reflection_session.goals_created = goals_created
                if reflection_depth is not None:
                    reflection_session.reflection_depth = reflection_depth
                if duration_seconds is not None:
                    reflection_session.duration_seconds = duration_seconds
                if analysis_results is not None:
                    reflection_session.analysis_results = analysis_results
                
                logger.info(f"Reflection session updated: {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating reflection session: {str(e)}", exc_info=True)
            return False

    def get_reflection_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        ID'ye göre yansıtma oturumunu getir
        
        Args:
            session_id: Oturum ID'si
            
        Returns:
            Dict: Yansıtma oturumu bilgileri veya None
        """
        try:
            with db_session() as session:
                reflection_session = session.query(ReflectionSession).filter(
                    ReflectionSession.id == session_id
                ).first()
                
                if not reflection_session:
                    return None
                
                return {
                    'id': str(reflection_session.id),
                    'user_id': str(reflection_session.user_id),
                    'reflection_type': reflection_session.reflection_type,
                    'trigger_reasons': reflection_session.trigger_reasons,
                    'analysis_results': reflection_session.analysis_results,
                    'insights_generated': reflection_session.insights_generated,
                    'goals_created': reflection_session.goals_created,
                    'reflection_depth': reflection_session.reflection_depth,
                    'created_at': reflection_session.created_at.isoformat() if reflection_session.created_at else None,
                    'duration_seconds': reflection_session.duration_seconds
                }
                
        except Exception as e:
            logger.error(f"Error getting reflection session by ID: {str(e)}", exc_info=True)
            return None

    def update_goal_status(self, goal_id: str, status: str, 
                          progress_metrics: Optional[Dict[str, Any]] = None,
                          completion_date: Optional[datetime] = None) -> bool:
        """
        Hedef durumunu güncelle
        
        Args:
            goal_id: Hedef ID'si
            status: Yeni durum ('active', 'completed', 'paused')
            progress_metrics: İlerleme metrikleri
            completion_date: Tamamlanma tarihi
            
        Returns:
            bool: Güncelleme başarılı mı
        """
        try:
            with db_session() as session:
                goal = session.query(EmergentGoal).filter(
                    EmergentGoal.id == goal_id
                ).first()
                
                if not goal:
                    logger.warning(f"Goal not found: {goal_id}")
                    return False
                
                goal.status = status
                if progress_metrics is not None:
                    goal.progress_metrics = progress_metrics
                if completion_date is not None:
                    goal.completion_date = completion_date
                elif status == 'completed' and not goal.completion_date:
                    goal.completion_date = datetime.now()
                
                logger.info(f"Goal status updated: {goal_id} -> {status}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating goal status: {str(e)}", exc_info=True)
            return False

    def update_insight_action_status(self, insight_id: str, acted_upon: bool,
                                   action_results: Optional[Dict[str, Any]] = None) -> bool:
        """
        İçgörü aksiyon durumunu güncelle
        
        Args:
            insight_id: İçgörü ID'si
            acted_upon: Aksiyon alındı mı
            action_results: Aksiyon sonuçları
            
        Returns:
            bool: Güncelleme başarılı mı
        """
        try:
            with db_session() as session:
                insight = session.query(AutonomousInsight).filter(
                    AutonomousInsight.id == insight_id
                ).first()
                
                if not insight:
                    logger.warning(f"Insight not found: {insight_id}")
                    return False
                
                insight.acted_upon = acted_upon
                if action_results is not None:
                    insight.action_results = action_results
                
                logger.info(f"Insight action status updated: {insight_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating insight action status: {str(e)}", exc_info=True)
            return False

    def get_user_reflection_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Kullanıcının yansıtma istatistiklerini getir
        
        Args:
            user_id: Kullanıcı ID'si
            days: Son kaç günün istatistikleri
            
        Returns:
            Dict: İstatistik bilgileri
        """
        try:
            with db_session() as session:
                since_date = datetime.now() - timedelta(days=days)
                
                # Yansıtma oturumu sayısı
                session_count = session.query(ReflectionSession).filter(
                    and_(
                        ReflectionSession.user_id == user_id,
                        ReflectionSession.created_at >= since_date
                    )
                ).count()
                
                # İçgörü sayısı
                insight_count = session.query(AutonomousInsight).filter(
                    and_(
                        AutonomousInsight.user_id == user_id,
                        AutonomousInsight.created_at >= since_date
                    )
                ).count()
                
                # Aktif hedef sayısı
                active_goal_count = session.query(EmergentGoal).filter(
                    and_(
                        EmergentGoal.user_id == user_id,
                        EmergentGoal.status == 'active'
                    )
                ).count()
                
                # Tamamlanan hedef sayısı
                completed_goal_count = session.query(EmergentGoal).filter(
                    and_(
                        EmergentGoal.user_id == user_id,
                        EmergentGoal.status == 'completed',
                        EmergentGoal.completion_date >= since_date
                    )
                ).count()
                
                return {
                    'user_id': user_id,
                    'period_days': days,
                    'reflection_sessions': session_count,
                    'insights_generated': insight_count,
                    'active_goals': active_goal_count,
                    'completed_goals': completed_goal_count,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting user reflection stats: {str(e)}", exc_info=True)
            return {
                'user_id': user_id,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }